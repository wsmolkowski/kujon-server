# coding=UTF-8

import logging
from datetime import datetime, timedelta

from bson import ObjectId
from tornado import auth, gen, web, escape
from tornado.ioloop import IOLoop

from api.handlers.base import BaseHandler, ApiHandler
from commons import constants, decorators
from commons.enumerators import ExceptionTypes, UserTypes
from commons.errors import AuthenticationError
from commons.mixins.JSendMixin import JSendMixin
from commons.mixins.OAuth2Mixin import OAuth2Mixin
from commons.mixins.SocialMixin import SocialMixin
from crawler import email_factory
from crawler import job_factory


class ArchiveHandler(ApiHandler):
    async def db_email_archive_user(self, recipient):
        email_job = email_factory.email_job(
            'Usunęliśmy Twoje konto w Kujon.mobi',
            self.config.SMTP_EMAIL,
            recipient if type(recipient) is list else [recipient],
            '\nCześć,'
            '\nTwoje konto w Kujon.mobi zostało skasowane, zastanów się czy nie wrócić do nas.\n'
            '\nPozdrawiamy,'
            '\nzespół Kujon.mobi'
            '\nemail: {0}\n'.format(self.config.SMTP_EMAIL)
        )

        await self.db_insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

    @decorators.authenticated
    @web.asynchronous
    async def post(self):
        try:
            user_doc = self.get_current_user()

            await self.db_archive_user(user_doc[constants.MONGO_ID])

            self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)

            await self.db_email_archive_user(user_doc[constants.USER_EMAIL])

            self.success('Dane użytkownika usunięte.')
        except Exception as ex:
            await self.exc(ex)


class AuthenticationHandler(BaseHandler, JSendMixin):
    EXCEPTION_TYPE = ExceptionTypes.AUTHENTICATION.value

    def on_finish(self):
        IOLoop.current().spawn_callback(self.db_insert, constants.COLLECTION_REMOTE_IP_HISTORY, {
            constants.USER_ID: self.getUserId(return_object_id=True),
            constants.CREATED_TIME: datetime.now(),
            'host': self.request.host,
            'method': self.request.method,
            'path': self.request.path,
            'query': self.request.query,
            'remote_ip': self._context.remote_ip
        })


class LogoutHandler(AuthenticationHandler):
    @web.asynchronous
    def get(self):
        self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
        self.redirect(self.config.DEPLOY_WEB)

    @web.asynchronous
    def post(self):
        self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
        self.success('Użytkownik wylogowany.')


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
                user_doc[constants.USER_TYPE] = UserTypes.FACEBOOK.value
                user_doc[constants.USER_NAME] = access['name']
                user_doc[constants.USER_EMAIL] = access['email']
                user_doc[constants.USER_DEVICE_TYPE] = 'WWW'
                user_doc[constants.USER_DEVICE_ID] = None

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
            self.reset_user_cookie(user_doc[constants.MONGO_ID])

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
            self.redirect(self.config.DEPLOY_WEB)
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
                user_doc[constants.USER_TYPE] = UserTypes.GOOGLE.value
                user_doc[constants.USER_NAME] = user['name']
                user_doc[constants.USER_EMAIL] = user['email']
                user_doc[constants.USOS_PAIRED] = False
                user_doc[constants.USER_DEVICE_TYPE] = 'WWW'
                user_doc[constants.USER_DEVICE_ID] = None
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
                user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_doc})

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

            self.reset_user_cookie(user_doc[constants.MONGO_ID])
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

        device_type = self.get_argument('device_type', default=None)
        device_id = self.get_argument('device_id', default=None)

        new_user = False

        try:

            if login_type not in ['FB', 'WWW', 'GOOGLE', 'EMAIL', 'FACEBOOK']:
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

            if email and token and login_type == UserTypes.GOOGLE.value:
                google_token = yield self.google_token(token)
                google_token[constants.USER_TYPE] = login_type
                yield self.db_insert_token(google_token)
            elif email and token and login_type.upper() in (UserTypes.FACEBOOK.value, 'FB'):
                facebook_token = yield self.facebook_token(token)
                facebook_token[constants.USER_TYPE] = login_type
                yield self.db_insert_token(facebook_token)

            user_doc[constants.USOS_ID] = usos_doc[constants.USOS_ID]
            user_doc[constants.UPDATE_TIME] = datetime.now()

            if email:
                user_doc[constants.USER_EMAIL] = email
            if token:
                user_doc[constants.MOBI_TOKEN] = token

            if new_user:
                user_doc[constants.USER_TYPE] = login_type
                user_doc[constants.USER_DEVICE_TYPE] = device_type
                user_doc[constants.USER_DEVICE_ID] = device_id
                user_doc[constants.CREATED_TIME] = datetime.now()
                new_id = yield self.db_insert_user(user_doc)

                self.set_cookie(self.config.KUJON_MOBI_REGISTER, str(new_id))
            else:
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)
                self.set_cookie(self.config.KUJON_MOBI_REGISTER, str(user_doc[constants.MONGO_ID]))

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
    async def db_email_registration(self, user_doc, usos_name):

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

        await self.db_insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

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

            user_id = self.get_cookie(self.config.KUJON_MOBI_REGISTER)
            logging.info('verifying user: {0} for oauth_token: {1} and oauth_verifier: {2}'.format(
                user_id, oauth_token_key, oauth_token_key
            ))
            user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(user_id)})

            self.clear_cookie(self.config.KUJON_MOBI_REGISTER)

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

                self.clear_cookie(self.config.KUJON_MOBI_REGISTER)
                self.reset_user_cookie(user_doc[constants.MONGO_ID])
                self.redirect(self.config.DEPLOY_WEB)

            if user_doc:

                auth_user = yield self.get_authenticated_user()  # dict with access_token key/secret
                user_doc.update(auth_user)
                del (user_doc['access_token'])
                yield self.db_update_user(user_doc[constants.MONGO_ID], user_doc)

                user_doc = yield self.db_cookie_user_id(user_doc[constants.MONGO_ID])

                self.reset_user_cookie(user_doc[constants.MONGO_ID])

                yield self._create_jobs(user_doc)

                self.clear_cookie(self.config.KUJON_MOBI_REGISTER)

                header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
                header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

                if header_email or header_token:
                    logging.info('Finish register MOBI OK')
                    self.success('Udało się sparować konto USOS')
                else:
                    logging.info('Finish register WWW OK')
                    yield self.db_email_registration(user_doc, usos_doc[constants.USOS_NAME])
                    self.redirect(self.config.DEPLOY_WEB)
            else:
                self.redirect(self.config.DEPLOY_WEB)

        except Exception as ex:
            yield self.exc(ex)


class AbstractEmailHandler(AuthenticationHandler):
    def set_default_headers(self):
        if self.isMobileRequest():
            self.set_header('Access-Control-Allow-Origin', '*')
        else:
            self.set_header('Access-Control-Allow-Origin', self.config.DEPLOY_WEB)
        self.set_header('Access-Control-Allow-Methods', ', '.join(self.SUPPORTED_METHODS))
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With')


class EmailRegisterHandler(AbstractEmailHandler):
    async def db_email_confirmation(self, email, user_id):

        confirmation_url = '{0}/authentication/email_confim/{1}'.format(self.config.DEPLOY_API,
                                                                        self.aes.encrypt(str(user_id)).decode())
        logging.debug('confirmation_url: {0}'.format(confirmation_url))

        message_text = '''\nCześć
            \nDziękujemy za utworzenie konta.
            \nAby zakończyć rejestrację kliknij na poniższy link:\n
            \n{0}
            \nPozdrawiamy,
            \nzespół {1}
            \nemail: {2}
        '''.format(confirmation_url, self.config.PROJECT_TITLE, self.config.SMTP_EMAIL)

        email_job = email_factory.email_job(
            '[{0}] Dokończ rejestrację konta'.format(self.config.PROJECT_TITLE),
            self.config.SMTP_EMAIL,
            email if type(email) is list else [email],
            message_text
        )

        await self.db_insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

        await self.db[constants.COLLECTION_MESSAGES].insert({
            constants.CREATED_TIME: datetime.now(),
            constants.FIELD_MESSAGE_FROM: self.config.PROJECT_TITLE,
            constants.FIELD_MESSAGE_TYPE: 'email',
            constants.FIELD_MESSAGE_TEXT: message_text
        })

    @web.asynchronous
    async def post(self):
        try:
            json_data = escape.json_decode(self.request.body.decode())

            if constants.USER_EMAIL not in json_data \
                    or constants.USER_PASSWORD not in json_data \
                    or constants.USER_DEVICE_TYPE not in json_data \
                    or constants.USER_DEVICE_ID not in json_data:
                raise AuthenticationError('Nie przekazano odpowiednich parametrów.')

            if 'password2' in json_data and json_data[constants.USER_PASSWORD] != json_data['password2']:
                raise AuthenticationError('Podane hasła nie zgadzają się.')

            if len(json_data[constants.USER_PASSWORD]) < 8:
                raise AuthenticationError('Podane hasło jest zbyt krótkie.')

            user_doc = await self.db_find_user_email(json_data[constants.USER_EMAIL])
            if user_doc:
                raise AuthenticationError(
                    'Podany adres email: {0} jest zajęty.'.format(json_data[constants.USER_EMAIL]))

            user_doc = dict()
            user_doc[constants.USER_TYPE] = UserTypes.EMAIL.value
            user_doc[constants.USER_NAME] = json_data[constants.USER_EMAIL]
            user_doc[constants.USER_EMAIL] = json_data[constants.USER_EMAIL]
            user_doc[constants.USER_DEVICE_TYPE] = json_data[constants.USER_DEVICE_TYPE]
            user_doc[constants.USER_DEVICE_ID] = json_data[constants.USER_DEVICE_ID]

            user_doc[constants.USER_PASSWORD] = self.aes.encrypt(json_data[constants.USER_PASSWORD])
            user_doc[constants.USOS_PAIRED] = False
            user_doc[constants.USER_EMAIL_CONFIRMED] = False
            user_doc[constants.USER_CREATED] = datetime.now()

            user_id = await self.db_insert_user(user_doc)
            self.reset_user_cookie(user_id)

            await self.db_email_confirmation(json_data[constants.USER_EMAIL], user_id)

            logging.debug('send confirmation email to new EMAIL user with id: {0} and email: {1}'.format(
                user_id, json_data[constants.USER_EMAIL]))

            self.success(
                'Dziękujemy za zarejestrowanie konta {0}. Aby aktywować konto należy postępować zgodnie z instrukcją przesłą w emailu weryfikacyjnym.'.format(
                    self.config.PROJECT_TITLE), cache_age=None)
        except Exception as ex:
            await self.exc(ex)


class EmailLoginHandler(AbstractEmailHandler):
    @web.asynchronous
    async def post(self):

        try:
            json_data = escape.json_decode(self.request.body)

            user_doc = await self.db_find_user_email(json_data[constants.USER_EMAIL])

            if not user_doc or user_doc[constants.USER_TYPE] != UserTypes.EMAIL.value or \
                            json_data[constants.USER_PASSWORD] != self.aes.decrypt(
                        user_doc[constants.USER_PASSWORD]).decode():
                raise AuthenticationError('Podano błędne dane.')

            if not user_doc[constants.USER_EMAIL_CONFIRMED]:
                raise AuthenticationError('Adres email nie został potwierdzony.')

            self.success(data={'token': self.aes.encrypt(str(user_doc[constants.MONGO_ID])).decode()})

        except Exception as ex:
            await self.exc(ex)


class EmailConfirmHandler(AuthenticationHandler):
    @web.asynchronous
    async def get(self, token):
        try:
            user_id = self.aes.decrypt(token.encode()).decode()
            user_doc = await self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: ObjectId(user_id)})

            if not user_doc:
                self.error(message='Błędny parametr wywołania.', code=403)
            elif constants.USER_EMAIL_CONFIRMED in user_doc and user_doc[constants.USER_EMAIL_CONFIRMED]:
                self.error(message='Token wykorzystany. Email potwierdzony.', code=403)
            else:
                user_doc[constants.USER_EMAIL_CONFIRMED] = True
                user_doc[constants.UPDATE_TIME] = datetime.now()

                await self.db_update_user(user_doc[constants.MONGO_ID], user_doc)
                self.redirect(self.config.DEPLOY_WEB)
        except Exception as ex:
            await self.exc(ex)
