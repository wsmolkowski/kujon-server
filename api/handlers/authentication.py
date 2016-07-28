# coding=UTF-8

import logging
from datetime import datetime, timedelta

from bson import ObjectId, json_util
from tornado import auth, gen, web, escape

from api.handlers.base import BaseHandler, ApiHandler
from commons import constants
from commons.errors import AuthenticationError
from commons.mixins.JSendMixin import JSendMixin
from commons.mixins.OAuth2Mixin import OAuth2Mixin
from commons.mixins.SocialMixin import SocialMixin
from crawler import email_factory
from crawler import job_factory


class ArchiveHandler(ApiHandler):
    @gen.coroutine
    def db_email_archive_user(self, recipient):
        email_job = email_factory.email_job(
            'Usunęliśmy Twoje konto w Kujon.mobi',
            self.config.SMTP_EMAIL,
            recipient if type(recipient) is list else [recipient],
            '\nCześć,'
            '\nTwoje konto w Kujon.mobi zostało skasowane, zastanów się czy nie wrócić do nas..\n'
            '\nPozdrawiamy,'
            '\nzespół Kujon.mobi'
            '\nemail: {0}\n'.format(self.config.SMTP_EMAIL)
        )

        yield self.db_insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

    # @web.asynchronous
    # @gen.coroutine
    # def get(self):
    #     user_doc = self.get_current_user()
    #
    #     if user_doc:
    #         yield self.db_archive_user(user_doc[constants.MONGO_ID])
    #
    #     self.clear_cookie(constants.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
    #     yield self.db_email_archive_user(user_doc[constants.USER_EMAIL])
    #     self.redirect(self.config.DEPLOY_WEB)

    @web.asynchronous
    @gen.coroutine
    def post(self):
        try:
            user_doc = self.get_current_user()

            if user_doc:
                yield self.db_archive_user(user_doc[constants.MONGO_ID])

            self.clear_cookie(constants.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
            yield self.db_email_archive_user(user_doc[constants.USER_EMAIL])

            self.success({})
        except Exception as ex:
            yield self.exc(ex)


class AuthenticationHandler(BaseHandler, JSendMixin):
    EXCEPTION_TYPE = 'authentication'

    @gen.coroutine
    def reset_user_cookie(self, user_doc):
        if constants.USER_NAME not in user_doc and constants.USER_EMAIL in user_doc:
            user_doc[constants.USER_NAME] = user_doc[constants.USER_EMAIL]

        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.set_secure_cookie(constants.KUJON_SECURE_COOKIE, escape.json_encode(json_util.dumps(user_doc)),
                               domain=self.config.SITE_DOMAIN)

        raise gen.Return()


class LogoutHandler(AuthenticationHandler):
    def get(self):
        self.clear_cookie(constants.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
        self.redirect(self.config.DEPLOY_WEB)


class FacebookOAuth2LoginHandler(AuthenticationHandler, auth.FacebookGraphMixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=self.config.DEPLOY_API + '/authentication/facebook',
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

                user_doc[constants.FACEBOOK] = dict()
                user_doc[constants.FACEBOOK][constants.FACEBOOK_NAME] = access[constants.FACEBOOK_NAME]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_EMAIL] = access[constants.FACEBOOK_EMAIL]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE] = access['picture']['data']['url']
                user_doc[constants.FACEBOOK][constants.FACEBOOK_ACCESS_TOKEN] = access[constants.FACEBOOK_ACCESS_TOKEN]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_ID] = access[constants.FACEBOOK_ID]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_SESSION_EXPIRES] = datetime.now() + timedelta(
                    seconds=int(access[constants.FACEBOOK_SESSION_EXPIRES][0]))

                user_doc[constants.USOS_PAIRED] = False
                user_doc[constants.USER_CREATED] = datetime.now()
                yield self.db_insert_user(user_doc)
            else:
                user_doc[constants.FACEBOOK] = dict()
                user_doc[constants.FACEBOOK][constants.FACEBOOK_NAME] = access[constants.FACEBOOK_NAME]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_EMAIL] = access[constants.FACEBOOK_EMAIL]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE] = access['picture']['data']['url']
                user_doc[constants.FACEBOOK][constants.FACEBOOK_ACCESS_TOKEN] = access[constants.FACEBOOK_ACCESS_TOKEN]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_ID] = access[constants.FACEBOOK_ID]
                user_doc[constants.FACEBOOK][constants.FACEBOOK_SESSION_EXPIRES] = datetime.now() + timedelta(
                    seconds=int(access[constants.FACEBOOK_SESSION_EXPIRES][0]))
                user_doc[constants.UPDATE_TIME] = datetime.now()
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)

            user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])
            yield self.reset_user_cookie(user_doc)

            self.redirect(self.config.DEPLOY_WEB)
        else:
            yield self.authorize_redirect(
                redirect_uri=self.config.DEPLOY_API + '/authentication/facebook',
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
            self.redirect(self.config.DEPLOY_WEB + '/')
            return

        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=self.config.DEPLOY_API + '/authentication/google',
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

            yield self.reset_user_cookie(user_doc)
            self.redirect(self.config.DEPLOY_WEB)

        else:
            yield self.authorize_redirect(
                redirect_uri=self.config.DEPLOY_API + '/authentication/google',
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class UsosRegisterHandler(AuthenticationHandler, SocialMixin, OAuth2Mixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        email = self.get_argument('email', default=None)
        token = self.get_argument('token', default=None)
        usos_id = self.get_argument('usos_id', default=None)
        login_type = self.get_argument('type', default=None)
        new_user = False

        try:

            if login_type not in ['FB', 'WWW', 'GOOGLE']:
                raise AuthenticationError('Nieznany typ logowania.')

            usos_doc = yield self.db_get_usos(usos_id)

            if not usos_doc:
                raise AuthenticationError('Nieznany USOS {0}'.format(usos_id))

            self.set_up(usos_doc)

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

            if email and token and login_type == 'GOOGLE':
                google_token = yield self.google_token(token)
                google_token['login_type'] = login_type
                yield self.db_insert_token(google_token)
            elif email and token and login_type.upper() == 'FB':
                facebook_token = yield self.facebook_token(token)
                facebook_token['login_type'] = login_type
                yield self.db_insert_token(facebook_token)

            user_doc[constants.USOS_ID] = usos_doc[constants.USOS_ID]
            user_doc[constants.UPDATE_TIME] = datetime.now()

            if email:
                user_doc[constants.USER_EMAIL] = email
            if token:
                user_doc[constants.MOBI_TOKEN] = token

            if new_user:
                user_doc['login_type'] = login_type
                user_doc[constants.CREATED_TIME] = datetime.now()
                new_id = yield self.db_insert_user(user_doc)

                self.set_cookie(constants.KUJON_MOBI_REGISTER, str(new_id))
            else:
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)
                self.set_cookie(constants.KUJON_MOBI_REGISTER, str(user_doc[constants.MONGO_ID]))

            yield self.authorize_redirect(extra_params={
                'scopes': 'studies|offline_access|student_exams|grades|crstests',
                'oauth_callback': self.config.DEPLOY_API + '/authentication/verify'
            })

        except Exception as ex:
            if login_type and login_type.upper() == 'WWW':
                yield self.exc(ex, finish=False)
                self.redirect(self.config.DEPLOY_WEB)
            else:
                yield self.exc(ex)


class UsosVerificationHandler(AuthenticationHandler, OAuth2Mixin):
    @gen.coroutine
    def db_email_registration(self, user_doc, usos_name):

        recipient = user_doc[constants.USER_EMAIL]

        email_job = email_factory.email_job(
            'Rejestracja w Kujon.mobi',
            self.config.SMTP_EMAIL,
            recipient if type(recipient) is list else [recipient],
            '\nCześć,\n'
            '\nRejestracja Twojego konta i połączenie z {0} zakończona pomyślnie.\n'
            '\nW razie pytań lub pomysłów na zmianę - napisz do nas. dzięki Tobie Kujon będzie lepszy.\n'
            '\nPozdrawiamy,'
            '\nzespół Kujon.mobi'
            '\nemail: {1}\n'.format(usos_name, self.config.SMTP_EMAIL)
        )

        yield self.db_insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

    @gen.coroutine
    def _create_jobs(self, user_doc):
        yield self.db_insert(constants.COLLECTION_JOBS_QUEUE,
                             job_factory.subscribe_user_job(user_doc[constants.MONGO_ID]))
        yield self.db_insert(constants.COLLECTION_JOBS_QUEUE,
                             job_factory.initial_user_job(user_doc[constants.MONGO_ID]))

    @web.asynchronous
    @gen.coroutine
    def get(self):
        oauth_token_key = self.get_argument('oauth_token', default=None)
        oauth_verifier = self.get_argument('oauth_verifier', default=None)

        try:
            if not oauth_token_key or not oauth_verifier:
                raise AuthenticationError('Jeden z podanych parametrów jest niepoprawny.')

            user_id = self.get_cookie(constants.KUJON_MOBI_REGISTER)
            logging.info('verifying user: {0} for oauth_token: {1} and oauth_verifier: {2}'.format(
                user_id, oauth_token_key, oauth_token_key
            ))
            user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(user_id)})

            self.clear_cookie(constants.KUJON_MOBI_REGISTER)

            usos_doc = yield self.db_get_usos(user_doc[constants.USOS_ID])

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
                yield self.reset_user_cookie(user_doc)
                self.redirect(self.config.DEPLOY_WEB)

            if user_doc:

                auth_user = yield self.get_authenticated_user()  # dict with access_token key/secret
                user_doc.update(auth_user)
                del (user_doc['access_token'])
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)

                user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])

                yield self.reset_user_cookie(user_doc)

                yield self._create_jobs(user_doc)

                self.clear_cookie(constants.KUJON_MOBI_REGISTER)

                header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
                header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

                if header_email or header_token:
                    logging.info('zakonczona rejestracja MOBI')
                    self.success('Udało się sparować konto USOS')
                else:
                    logging.info('zakonczona rejestracja WWW')
                    yield self.db_email_registration(user_doc, usos_doc[constants.USOS_NAME])
                    self.redirect(self.config.DEPLOY_WEB)
            else:
                self.redirect(self.config.DEPLOY_WEB)

        except Exception as ex:
            yield self.exc(ex)
