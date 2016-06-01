# coding=UTF-8

import copy
import logging
from datetime import datetime, timedelta

from bson import ObjectId, json_util
from tornado import auth, gen, web, escape

from base import BaseHandler, ApiHandler
from commons import constants, settings, decorators
from commons.errors import AuthenticationError
from commons.mixins.GoogleMixin import GoogleMixin
from commons.mixins.JSendMixin import JSendMixin
from commons.mixins.OAuth2Mixin import OAuth2Mixin
from crawler import email_factory
from crawler import job_factory


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(constants.KUJON_SECURE_COOKIE, domain=settings.SITE_DOMAIN)
        self.redirect(settings.DEPLOY_WEB)


class ArchiveHandler(ApiHandler):
    @gen.coroutine
    def db_email_archive_user(self, recipient):
        email_job = email_factory.email_job(
            'Usunęliśmy Twoje konto w Kujon.mobi',
            settings.SMTP_EMAIL,
            recipient if type(recipient) is list else [recipient],
            '\nCześć,'
            '\nTwoje konto w Kujon.mobi zostało skasowane, zastanów się czy nie wrócić do nas..\n'
            '\nPozdrawiamy,'
            '\nzespół Kujon.mobi'
            '\nemail: {0}\n'.format(settings.SMTP_EMAIL)
        )

        yield self.db_insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        user_doc = self.get_current_user()
        if user_doc:
            yield self.db_archive_user(user_doc[constants.MONGO_ID])

        self.clear_cookie(constants.KUJON_SECURE_COOKIE, domain=settings.SITE_DOMAIN)
        yield self.db_email_archive_user(user_doc[constants.USER_EMAIL])
        self.redirect(settings.DEPLOY_WEB)


class AuthenticationHandler(BaseHandler, JSendMixin):
    EXCEPTION_TYPE = 'authentication'

    def reset_user_cookie(self, user_doc):
        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.set_secure_cookie(constants.KUJON_SECURE_COOKIE, escape.json_encode(json_util.dumps(user_doc)),
                               domain=settings.SITE_DOMAIN)

    _usoses = list()

    @gen.coroutine
    def get_usoses(self, showtokens):

        if not self._usoses:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})

            while (yield cursor.fetch_next):
                usos = cursor.next_object()
                usos['logo'] = settings.DEPLOY_WEB + usos['logo']

                if settings.ENCRYPT_USOSES_KEYS:
                    usos = dict(self.aes.decrypt_usos(usos))

                self._usoses.append(usos)

        result_usoses = copy.deepcopy(self._usoses)
        if not showtokens:
            for usos in result_usoses:
                usos.pop("consumer_secret")
                usos.pop("consumer_key")
                usos.pop("enabled")
                usos.pop("contact")
                usos.pop("url")
        raise gen.Return(result_usoses)

    @gen.coroutine
    def get_usos(self, key, value):
        usoses = yield self.get_usoses(showtokens=True)

        for u in usoses:
            if u[key] == value:
                raise gen.Return(u)
        raise gen.Return(None)


class FacebookOAuth2LoginHandler(AuthenticationHandler, auth.FacebookGraphMixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=settings.DEPLOY_API + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                client_secret=self.settings['facebook_oauth']['secret'],
                code=self.get_argument('code'),
                extra_fields={'email', 'id'})

            user_doc = yield self.db_find_user_email(access['email'])

            if not user_doc:
                user_doc = dict()
                user_doc[constants.USER_TYPE] = 'facebook'
                user_doc[constants.USER_NAME] = access['name']
                user_doc[constants.USER_EMAIL] = access['email']

                user_doc[constants.FB] = dict()
                user_doc[constants.FB][constants.FB_NAME] = access[constants.FB_NAME]
                user_doc[constants.FB][constants.FB_EMAIL] = access[constants.FB_EMAIL]
                user_doc[constants.FB][constants.FB_PICTURE] = access['picture']['data']['url']
                user_doc[constants.FB][constants.FB_ACCESS_TOKEN] = access[constants.FB_ACCESS_TOKEN]
                user_doc[constants.FB][constants.FB_ID] = access[constants.FB_ID]
                user_doc[constants.FB][constants.FB_SESSION_EXPIRES] = datetime.now() + timedelta(
                    seconds=int(access[constants.FB_SESSION_EXPIRES][0]))

                user_doc[constants.USOS_PAIRED] = False
                user_doc[constants.USER_CREATED] = datetime.now()
                yield self.db_insert_user(user_doc)
            else:
                user_doc[constants.FB] = dict()
                user_doc[constants.FB][constants.FB_NAME] = access[constants.FB_NAME]
                user_doc[constants.FB][constants.FB_EMAIL] = access[constants.FB_EMAIL]
                user_doc[constants.FB][constants.FB_PICTURE] = access['picture']['data']['url']
                user_doc[constants.FB][constants.FB_ACCESS_TOKEN] = access[constants.FB_ACCESS_TOKEN]
                user_doc[constants.FB][constants.FB_ID] = access[constants.FB_ID]
                user_doc[constants.FB][constants.FB_SESSION_EXPIRES] = datetime.now() + timedelta(
                    seconds=int(access[constants.FB_SESSION_EXPIRES][0]))
                user_doc[constants.UPDATE_TIME] = datetime.now()
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)

            user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])
            self.reset_user_cookie(user_doc)

            # + '?token={0}'.format(user_doc[constants.MONGO_ID])
            self.redirect(settings.DEPLOY_WEB)
        else:
            yield self.authorize_redirect(
                redirect_uri=settings.DEPLOY_API + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                scope=['public_profile', 'email', 'user_friends'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class GoogleOAuth2LoginHandler(AuthenticationHandler, auth.GoogleOAuth2Mixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):

        if self.get_argument('error', False):
            logging.error('Błąd autoryzacji Google+.')
            self.redirect(settings.DEPLOY_WEB + '/')
            return

        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=settings.DEPLOY_API + '/authentication/google',
                code=self.get_argument('code'))
            user = yield self.oauth2_request(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                access_token=access['access_token'])

            user_doc = yield self.db_find_user_email(user['email'])
            if not user_doc:
                user_doc = dict()
                user_doc[constants.USER_TYPE] = 'google'
                user_doc[constants.USER_NAME] = user['name']
                user_doc[constants.USER_EMAIL] = user['email']
                user_doc[constants.USOS_PAIRED] = False
                user_doc[constants.USER_CREATED] = datetime.now()

                user_doc[constants.GOOGLE] = dict()
                user_doc[constants.GOOGLE][constants.GOOGLE_NAME] = user[constants.GOOGLE_NAME]
                user_doc[constants.GOOGLE][constants.GOOGLE_EMAIL] = user[constants.GOOGLE_EMAIL]
                user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE] = user[constants.GOOGLE_PICTURE]
                user_doc[constants.GOOGLE][constants.GOOGLE_ACCESS_TOKEN] = access[constants.GOOGLE_ACCESS_TOKEN]
                user_doc[constants.GOOGLE][constants.GOOGLE_EXPIRES_IN] = datetime.now() + timedelta(
                    seconds=access[constants.GOOGLE_EXPIRES_IN])
                user_doc[constants.GOOGLE][constants.GOOGLE_ID_TOKEN] = access[constants.GOOGLE_ID_TOKEN]
                user_doc[constants.GOOGLE][constants.GOOGLE_TOKEN_TYPE] = access[constants.GOOGLE_TOKEN_TYPE]

                user_doc = yield self.db_insert_user(user_doc)
                user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                    {constants.MONGO_ID: user_doc}, constants.COOKIE_FIELDS)
                user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])

            else:
                user_doc[constants.GOOGLE] = dict()
                user_doc[constants.GOOGLE][constants.GOOGLE_NAME] = user[constants.GOOGLE_NAME]
                user_doc[constants.GOOGLE][constants.GOOGLE_EMAIL] = user[constants.GOOGLE_EMAIL]
                user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE] = user[constants.GOOGLE_PICTURE]
                user_doc[constants.GOOGLE][constants.GOOGLE_ACCESS_TOKEN] = access[constants.GOOGLE_ACCESS_TOKEN]
                user_doc[constants.GOOGLE][constants.GOOGLE_EXPIRES_IN] = datetime.now() + timedelta(
                    seconds=access[constants.GOOGLE_EXPIRES_IN])
                user_doc[constants.GOOGLE][constants.GOOGLE_ID_TOKEN] = access[constants.GOOGLE_ID_TOKEN]
                user_doc[constants.GOOGLE][constants.GOOGLE_TOKEN_TYPE] = access[constants.GOOGLE_TOKEN_TYPE]

                user_doc[constants.UPDATE_TIME] = datetime.now()

                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)
                user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])

            self.reset_user_cookie(user_doc)
            self.redirect(settings.DEPLOY_WEB)

        else:
            yield self.authorize_redirect(
                redirect_uri=settings.DEPLOY_API + '/authentication/google',
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class UsosRegisterHandler(AuthenticationHandler, GoogleMixin, OAuth2Mixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        email = self.get_argument('email', default=None, strip=True)
        token = self.get_argument('token', default=None, strip=True)
        usos_id = self.get_argument('usos_id', default=None, strip=True)
        new_user = False

        try:
            usos_doc = yield self.get_usos(constants.USOS_ID, usos_id)

            if email:
                user_doc = yield self.db_find_user_email(email)
                if not user_doc:
                    user_doc = dict()
                    new_user = True
            else:
                user_doc = yield self.db_find_user()
                if not user_doc:
                    raise AuthenticationError('Użytkownik musi posiadać konto. Prośba o zalogowanie.')

                if constants.USOS_PAIRED in user_doc and user_doc[constants.USOS_PAIRED]:
                    raise AuthenticationError(
                        'Użytkownik jest już zarejestrowany w {0}.'.format(user_doc[constants.USOS_ID]))

            if email and token:
                google_token = yield self.google_token(token)
                yield self.db_insert_token(google_token)

            if not usos_doc:
                self.fail('Nieznany USOS {0}'.format(usos_id))
                return

            self.set_up(usos_doc)

            user_doc[constants.USOS_ID] = usos_doc[constants.USOS_ID]
            user_doc[constants.UPDATE_TIME] = datetime.now()

            if email:
                user_doc[constants.USER_EMAIL] = email
            if token:
                user_doc[constants.MOBI_TOKEN] = token

            if new_user:
                user_doc[constants.CREATED_TIME] = datetime.now()
                new_id = yield self.db_insert_user(user_doc)
                logging.info('insert: ' + str(new_id))
                self.set_cookie(constants.KUJON_MOBI_REGISTER, str(new_id))
            else:
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)
                self.set_cookie(constants.KUJON_MOBI_REGISTER, str(user_doc[constants.MONGO_ID]))

            logging.info(settings.DEPLOY_API + '/authentication/verify')

            yield self.authorize_redirect(extra_params={
                'scopes': 'studies|offline_access|student_exams|grades',
                'oauth_callback': settings.DEPLOY_API + '/authentication/verify'
            })

        except Exception, ex:
            yield self.exc(ex)


class UsosVerificationHandler(AuthenticationHandler, OAuth2Mixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        oauth_token_key = self.get_argument('oauth_token', default=None, strip=True)
        oauth_verifier = self.get_argument('oauth_verifier', default=None, strip=True)

        try:
            if not oauth_token_key or not oauth_verifier:
                raise AuthenticationError('Jeden z podanych parametrów jest niepoprawny.')

            user_id = self.get_cookie(constants.KUJON_MOBI_REGISTER)
            logging.info('verifying user: {0} for oauth_token: {1} and oauth_verifier: {2}'.format(
                user_id, oauth_token_key, oauth_token_key
            ))
            user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(user_id)})

            self.clear_cookie(constants.KUJON_MOBI_REGISTER)

            usos_doc = yield self.get_usos(constants.USOS_ID, user_doc[constants.USOS_ID])

            self.set_up(usos_doc)

            if self.get_argument('error', False):
                updated_user = user_doc
                updated_user[constants.USOS_PAIRED] = False
                updated_user[constants.ACCESS_TOKEN_SECRET] = None
                updated_user[constants.ACCESS_TOKEN_KEY] = None
                updated_user[constants.UPDATE_TIME] = datetime.now()
                updated_user[constants.OAUTH_VERIFIER] = None

                yield self.db_update_user(user_doc[constants.MONGO_ID], updated_user)

                user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])

                self.clear_cookie(constants.KUJON_MOBI_REGISTER)
                self.reset_user_cookie(user_doc)
                self.redirect(settings.DEPLOY_WEB)

            if user_doc:

                auth_user = yield self.get_authenticated_user()  # dict with access_token key/secret
                user_doc.update(auth_user)
                del (user_doc['access_token'])
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)

                user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])

                self.reset_user_cookie(user_doc)

                self.db_insert(constants.COLLECTION_JOBS_QUEUE,
                               job_factory.initial_user_job(user_doc[constants.MONGO_ID]))

                self.clear_cookie(constants.KUJON_MOBI_REGISTER)

                header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
                header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

                if header_email or header_token:
                    logging.info('zakonczona rejestracja MOBI')
                    self.success('Udało się sparować konto USOS')
                else:
                    logging.info('zakonczona rejestracja WWW')
                    yield self.db_email_registration(user_doc)
                    self.redirect(settings.DEPLOY_WEB)
            else:
                self.redirect(settings.DEPLOY_WEB)

        except Exception, ex:
            yield self.exc(ex)
