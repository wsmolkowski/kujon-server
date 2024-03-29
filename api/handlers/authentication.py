# coding=UTF-8

import json
import logging
from datetime import datetime, timedelta

from bson import ObjectId
from tornado import auth, escape, gen
from tornado.ioloop import IOLoop

from api.handlers.base.api import ApiHandler
from api.handlers.base.base import BaseHandler
from api.mixins.OAuth2Mixin import OAuth2Mixin
from commons import decorators
from commons.constants import collections, fields, config
from commons.enumerators import ExceptionTypes, UserTypes
from commons.errors import AuthenticationError


class ArchiveHandler(BaseHandler):
    async def _removeUserData(self, skip_collections=None, user_id=None):
        if not user_id:
            user_id = self.getUserId()

        if not skip_collections:
            skip_collections = list()

        try:
            collections = await self.db.collection_names(include_system_collections=False)
            remove_tasks = list()
            for collection in collections:

                if collection in skip_collections:
                    continue

                exists = await self.db[collection].find_one({fields.USER_ID: {'$exists': True, '$ne': False}})
                if exists:
                    remove_tasks.append(self.db[collection].remove({fields.USER_ID: user_id}))

            result = await gen.multi(remove_tasks)
            logging.info('removed user data for user_id: {0} resulted in: {1}'.format(user_id, result))
        except Exception as ex:
            logging.exception(ex)

    @decorators.authenticated
    async def post(self):
        try:
            user_doc = self.get_current_user()

            user_doc[fields.USER_ID] = user_doc.pop(fields.MONGO_ID)

            await self.db_insert(collections.USERS_ARCHIVE, user_doc)

            await self.db_remove(collections.USERS,
                                 {fields.MONGO_ID: user_doc[fields.USER_ID]},
                                 force=True)

            self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)

            IOLoop.current().spawn_callback(self._unsubscribeUsos, )
            IOLoop.current().spawn_callback(self._removeUserData, [collections.USERS_ARCHIVE, ], self.getUserId())
            IOLoop.current().spawn_callback(self.email_archive_user, user_doc[fields.USER_EMAIL])

            self.success('Dane użytkownika usunięte.')
        except Exception as ex:
            await self.exc(ex)


class AuthenticationHandler(BaseHandler):
    EXCEPTION_TYPE = ExceptionTypes.AUTHENTICATION.value

    def on_finish(self):
        IOLoop.current().spawn_callback(self.db_insert, collections.REMOTE_IP_HISTORY, {
            fields.USER_ID: self.getUserId(),
            fields.CREATED_TIME: datetime.now(),
            'host': self.request.host,
            'method': self.request.method,
            'path': self.request.path,
            'query': self.request.query,
            'remote_ip': self._context.remote_ip
        })

    async def db_cookie_user_id(self, user_id):
        user_doc = await self.db[collections.USERS].find_one({fields.MONGO_ID: user_id})

        if fields.GOOGLE in user_doc:
            user_doc[fields.PICTURE] = user_doc[fields.GOOGLE][fields.GOOGLE_PICTURE]
            del (user_doc[fields.GOOGLE])

        if fields.FACEBOOK in user_doc:
            user_doc[fields.PICTURE] = user_doc[fields.FACEBOOK][fields.FACEBOOK_PICTURE]
            del (user_doc[fields.FACEBOOK])

        return user_doc


class LogoutHandler(AuthenticationHandler):
    async def remove_token(self):
        user_doc = self.get_current_user()
        if user_doc and fields.USER_EMAIL in user_doc:
            await self.db_remove_token(user_doc[fields.USER_EMAIL], user_doc[fields.USER_TYPE])

    async def get(self):
        self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
        await self.remove_token()
        self.redirect(self.config.DEPLOY_WEB)

    async def post(self):
        self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
        await self.remove_token()
        self.success('Użytkownik wylogowany.')


class FacebookOAuth2LoginHandler(AuthenticationHandler, auth.FacebookGraphMixin):
    async def get(self):
        if self.get_argument('code', False):
            access = await self.get_authenticated_user(
                redirect_uri=self.config.DEPLOY_API + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                client_secret=self.settings['facebook_oauth']['secret'],
                code=self.get_argument('code'),
                extra_fields={'email', 'id'})

            user_doc = await self.findUserByEmail(access['email'])

            if not user_doc:
                user_doc = dict()
                user_doc[fields.USER_TYPE] = UserTypes.FACEBOOK.value
                user_doc[fields.USER_NAME] = access['name']
                user_doc[fields.USER_EMAIL] = access['email']
                user_doc[fields.USER_DEVICE_TYPE] = 'WWW'
                user_doc[fields.USER_DEVICE_ID] = None

                user_doc[fields.FACEBOOK] = dict()
                user_doc[fields.FACEBOOK][fields.FACEBOOK_NAME] = access[fields.FACEBOOK_NAME]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_EMAIL] = access[fields.FACEBOOK_EMAIL]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_PICTURE] = access['picture']['data']['url']
                user_doc[fields.FACEBOOK][fields.FACEBOOK_ACCESS_TOKEN] = access[fields.FACEBOOK_ACCESS_TOKEN]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_ID] = access[fields.FACEBOOK_ID]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_SESSION_EXPIRES] = datetime.now() + timedelta(
                    seconds=int(access[fields.FACEBOOK_SESSION_EXPIRES][0]))

                user_doc[fields.USOS_PAIRED] = False
                user_doc[fields.USER_CREATED] = datetime.now()
                await self.db_insert_user(user_doc)
            else:
                user_doc[fields.FACEBOOK] = dict()
                user_doc[fields.FACEBOOK][fields.FACEBOOK_NAME] = access[fields.FACEBOOK_NAME]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_EMAIL] = access[fields.FACEBOOK_EMAIL]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_PICTURE] = access['picture']['data']['url']
                user_doc[fields.FACEBOOK][fields.FACEBOOK_ACCESS_TOKEN] = access[fields.FACEBOOK_ACCESS_TOKEN]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_ID] = access[fields.FACEBOOK_ID]
                user_doc[fields.FACEBOOK][fields.FACEBOOK_SESSION_EXPIRES] = datetime.now() + timedelta(
                    seconds=int(access[fields.FACEBOOK_SESSION_EXPIRES][0]))
                user_doc[fields.UPDATE_TIME] = datetime.now()
                await self.db_update_user(user_doc[fields.MONGO_ID], user_doc)

            user_doc = await self.db_cookie_user_id(user_doc[fields.MONGO_ID])
            self.reset_user_cookie(user_doc[fields.MONGO_ID])

            self.redirect(self.config.DEPLOY_WEB)
        else:
            await self.authorize_redirect(
                redirect_uri=self.config.DEPLOY_API + '/authentication/facebook',
                client_id=self.settings['facebook_oauth']['key'],
                scope=['public_profile', 'email', 'user_friends'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class GoogleOAuth2LoginHandler(AuthenticationHandler, auth.GoogleOAuth2Mixin):
    async def get(self):

        if self.get_argument('error', False):
            logging.error('Błąd autoryzacji Google+.')
            self.redirect(self.config.DEPLOY_WEB)
            return

        if self.get_argument('code', False):
            access = await self.get_authenticated_user(
                redirect_uri=self.config.DEPLOY_API + '/authentication/google',
                code=self.get_argument('code'))
            user = await self.oauth2_request(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                access_token=access['access_token'])

            user_doc = await self.findUserByEmail(user['email'])
            if not user_doc:
                user_doc = dict()
                user_doc[fields.USER_TYPE] = UserTypes.GOOGLE.value
                user_doc[fields.USER_NAME] = user['name']
                user_doc[fields.USER_EMAIL] = user['email']
                user_doc[fields.USOS_PAIRED] = False
                user_doc[fields.USER_DEVICE_TYPE] = 'WWW'
                user_doc[fields.USER_DEVICE_ID] = None
                user_doc[fields.USER_CREATED] = datetime.now()

                user_doc[fields.GOOGLE] = dict()
                user_doc[fields.GOOGLE][fields.GOOGLE_NAME] = user[fields.GOOGLE_NAME]
                user_doc[fields.GOOGLE][fields.GOOGLE_EMAIL] = user[fields.GOOGLE_EMAIL]
                user_doc[fields.GOOGLE][fields.GOOGLE_PICTURE] = user[fields.GOOGLE_PICTURE]
                user_doc[fields.GOOGLE][fields.GOOGLE_ACCESS_TOKEN] = access[fields.GOOGLE_ACCESS_TOKEN]
                user_doc[fields.GOOGLE][fields.GOOGLE_EXPIRES_IN] = datetime.now() + timedelta(
                    seconds=access[fields.GOOGLE_EXPIRES_IN])
                user_doc[fields.GOOGLE][fields.GOOGLE_ID_TOKEN] = access[fields.GOOGLE_ID_TOKEN]
                user_doc[fields.GOOGLE][fields.GOOGLE_TOKEN_TYPE] = access[fields.GOOGLE_TOKEN_TYPE]

                user_doc = await self.db_insert_user(user_doc)
                user_doc = await self.db[collections.USERS].find_one({fields.MONGO_ID: user_doc})

            else:
                user_doc[fields.GOOGLE] = dict()
                user_doc[fields.GOOGLE][fields.GOOGLE_NAME] = user[fields.GOOGLE_NAME]
                user_doc[fields.GOOGLE][fields.GOOGLE_EMAIL] = user[fields.GOOGLE_EMAIL]
                user_doc[fields.GOOGLE][fields.GOOGLE_PICTURE] = user[fields.GOOGLE_PICTURE]
                user_doc[fields.GOOGLE][fields.GOOGLE_ACCESS_TOKEN] = access[fields.GOOGLE_ACCESS_TOKEN]
                user_doc[fields.GOOGLE][fields.GOOGLE_EXPIRES_IN] = datetime.now() + timedelta(
                    seconds=access[fields.GOOGLE_EXPIRES_IN])
                user_doc[fields.GOOGLE][fields.GOOGLE_ID_TOKEN] = access[fields.GOOGLE_ID_TOKEN]
                user_doc[fields.GOOGLE][fields.GOOGLE_TOKEN_TYPE] = access[fields.GOOGLE_TOKEN_TYPE]

                user_doc[fields.UPDATE_TIME] = datetime.now()

                await self.db_update_user(user_doc[fields.MONGO_ID], user_doc)
                user_doc = await self.db_cookie_user_id(user_doc[fields.MONGO_ID])

            self.reset_user_cookie(user_doc[fields.MONGO_ID])
            self.redirect(self.config.DEPLOY_WEB)

        else:
            await self.authorize_redirect(
                redirect_uri=self.config.DEPLOY_API + '/authentication/google',
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class UsosRegisterHandler(AuthenticationHandler, OAuth2Mixin):
    async def get(self):
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

            usos_doc = await self.db_get_usos(usos_id)

            if not usos_doc:
                raise AuthenticationError('Nieznany USOS {0}'.format(usos_id))

            self.oauth_set_up(usos_doc)

            if email:
                user_doc = await self.findUserByEmail(email)
                if not user_doc:
                    user_doc = dict()
                    new_user = True
            else:
                user_doc = await self.db_find_user()
                if not user_doc:
                    raise AuthenticationError('Użytkownik musi posiadać konto. Prośba o zalogowanie.')

                if fields.USOS_PAIRED in user_doc and user_doc[fields.USOS_PAIRED]:
                    raise AuthenticationError(
                        'Użytkownik jest już zarejestrowany w {0}.'.format(user_doc[fields.USOS_ID]))

            if email and token and login_type == UserTypes.GOOGLE.value:
                google_token = await self._context.socialCaller.google_token(token)
                google_token[fields.USER_TYPE] = login_type
                await self.db_insert_token(google_token)
            elif email and token and login_type.upper() in (UserTypes.FACEBOOK.value, 'FB'):
                facebook_token = await self._context.socialCaller.facebook_token(token)
                facebook_token[fields.USER_TYPE] = login_type
                await self.db_insert_token(facebook_token)

            user_doc[fields.USOS_ID] = usos_doc[fields.USOS_ID]
            user_doc[fields.UPDATE_TIME] = datetime.now()

            if email:
                user_doc[fields.USER_EMAIL] = email
            if token:
                user_doc[fields.MOBI_TOKEN] = token

            if new_user:
                user_doc[fields.USER_TYPE] = login_type
                user_doc[fields.USER_DEVICE_TYPE] = device_type
                user_doc[fields.USER_DEVICE_ID] = device_id
                user_doc[fields.CREATED_TIME] = datetime.now()
                new_id = await self.db_insert_user(user_doc)

                self.set_cookie(self.config.KUJON_MOBI_REGISTER, str(new_id))
            else:
                await self.db_update_user(user_doc[fields.MONGO_ID], user_doc)
                self.set_cookie(self.config.KUJON_MOBI_REGISTER, str(user_doc[fields.MONGO_ID]))

            await self.authorize_redirect(extra_params={
                'scopes': 'studies|offline_access|student_exams|grades|crstests',
                'oauth_callback': self.config.DEPLOY_API + '/authentication/verify'
            })

        except Exception as ex:
            if login_type and login_type.upper() == 'WWW':
                await self.exc(ex, finish=False)
                self.redirect(self.config.DEPLOY_WEB)
            else:
                await self.exc(ex)


class UsosVerificationHandler(AuthenticationHandler, OAuth2Mixin, ApiHandler):
    async def __process_crstests(self):
        crstests_doc = await self.api_crstests()

        grade_points = []
        for crstest in crstests_doc['tests']:
            grade_points.append(self.api_crstests_grades(crstest['node_id']))
            grade_points.append(self.api_crstests_points(crstest['node_id']))

        await gen.multi(grade_points)

    async def _user_crawl(self):
        try:
            user_info = await self.api_user_usos_info()
            await self.api_thesis(user_info=user_info)
            await self.api_terms()
            await self.api_programmes(user_info=user_info)
            await self.api_faculties(user_info=user_info)
            await self.__process_crstests()
        except Exception as ex:
            await self.exc(ex, finish=False)

    async def _subscribeUsos(self):

        await self._unsubscribeUsos()

        async def callUnitilSuccess(event_type, callback_url, verify_token):

            try_until = datetime.now() + timedelta(seconds=60 * 2)  # 60 usos subscribe timeout

            while True:
                try:
                    subscribe_doc = await self.usosCall(
                        path='services/events/subscribe_event',
                        arguments={
                            'event_type': event_type,
                            'callback_url': callback_url,
                            'verify_token': str(verify_token)
                        })

                    return subscribe_doc

                except Exception as ex:
                    if datetime.now() < try_until:
                        logging.warning(
                            'waiting for executing: {0} {1} {2}'.format(event_type, callback_url, verify_token))
                        await gen.sleep(60)
                        continue
                    raise ex

        try:
            current_subscriptions = await self.usosCall(path='services/events/subscriptions')
            if current_subscriptions and isinstance(current_subscriptions, list):
                current_subscriptions = json.dumps(current_subscriptions)
                current_subscriptions = escape.json_decode(current_subscriptions)

            logging.debug(
                'current subscriptions user: {0} {1}'.format(self.getUserId(), current_subscriptions))
        except Exception as ex:
            logging.exception(ex)
            current_subscriptions = list()

        if current_subscriptions:
            logging.debug('subscriptions exist for USOS: {0} not processing for user: {1}'.format(
                self.getUsosId(), self.getUserId()))
            return

        # setting subscriptions for given USOS
        for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
            try:
                callback_url = '{0}/{1}/{2}'.format(self.config.DEPLOY_EVENT,
                                                    self.getUsosId(),
                                                    event_type.split('/')[-1])

                verify_token = await self.db[collections.EVENTS_VERIFY_TOKENS].insert({
                    fields.USER_ID: self.getUserId(),
                    fields.EVENT_TYPE: event_type,
                    fields.CREATED_TIME: datetime.now()
                })

                subscribe_doc = await callUnitilSuccess(event_type, callback_url, str(verify_token))

                subscribe_doc['event_type'] = event_type
                subscribe_doc[fields.USER_ID] = self.getUserId()

                await self.db_insert(collections.SUBSCRIPTIONS, subscribe_doc)
            except Exception as ex:
                await self.exc(ex, finish=False)

    async def get(self):
        oauth_token_key = self.get_argument('oauth_token', default=None)
        oauth_verifier = self.get_argument('oauth_verifier', default=None)

        try:
            if not oauth_token_key or not oauth_verifier:
                raise AuthenticationError('Jeden z podanych parametrów jest niepoprawny.')

            user_id = self.get_cookie(self.config.KUJON_MOBI_REGISTER)

            if not user_id:
                raise AuthenticationError('Nie przekazano odpowiedniego ciasteczka.')

            logging.debug('verifying user: {0} for oauth_token: {1} and oauth_verifier: {2}'.format(
                user_id, oauth_token_key, oauth_token_key
            ))

            user_doc = await self.db[collections.USERS].find_one({fields.MONGO_ID: ObjectId(user_id)})

            if not user_doc:
                raise AuthenticationError('Nie znaleziono użytkownika.')

            self.clear_cookie(self.config.KUJON_MOBI_REGISTER)

            usos_doc = await self.db_get_usos(user_doc[fields.USOS_ID])

            self.oauth_set_up(usos_doc)

            if self.get_argument('error', False):
                updated_user = user_doc
                updated_user[fields.USOS_PAIRED] = False
                updated_user[fields.ACCESS_TOKEN_SECRET] = None
                updated_user[fields.ACCESS_TOKEN_KEY] = None
                updated_user[fields.UPDATE_TIME] = datetime.now()
                updated_user[fields.OAUTH_VERIFIER] = None

                await self.db_update_user(user_doc[fields.MONGO_ID], updated_user)

                user_doc = await self.db_cookie_user_id(user_doc[fields.MONGO_ID])

                self.clear_cookie(self.config.KUJON_MOBI_REGISTER)
                self.reset_user_cookie(user_doc[fields.MONGO_ID])
                self.redirect(self.config.DEPLOY_WEB)

            if user_doc:

                auth_user = await self.get_authenticated_user()  # dict with access_token key/secret
                user_doc.update(auth_user)
                del (user_doc['access_token'])
                await self.db_update_user(user_doc[fields.MONGO_ID], user_doc)

                user_doc = await self.db_cookie_user_id(user_doc[fields.MONGO_ID])

                self.reset_user_cookie(user_doc[fields.MONGO_ID])

                await self._buildContext()

                # gather user data from USOS and update context with usos_user_id needed for subscription
                await self.api_user_usos_info()
                await self._buildContext()

                IOLoop.current().spawn_callback(self._subscribeUsos, )
                IOLoop.current().spawn_callback(self._user_crawl, )

                self.clear_cookie(self.config.KUJON_MOBI_REGISTER)

                header_email = self.request.headers.get(config.MOBILE_X_HEADER_EMAIL, False)
                header_token = self.request.headers.get(config.MOBILE_X_HEADER_TOKEN, False)

                if header_email or header_token:
                    logging.debug('Finish register MOBI OK')
                    IOLoop.current().spawn_callback(self.email_registration, user_doc)
                    self.success('Udało się sparować konto USOS')
                else:
                    logging.debug('Finish register WWW OK')
                    IOLoop.current().spawn_callback(self.email_registration, user_doc)
                    self.redirect(self.config.DEPLOY_WEB)
            else:
                self.redirect(self.config.DEPLOY_WEB)

        except Exception as ex:
            await self.exc(ex)


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
    async def post(self):
        try:
            json_data = escape.json_decode(self.request.body.decode())

            if fields.USER_EMAIL not in json_data \
                    or fields.USER_PASSWORD not in json_data \
                    or fields.USER_DEVICE_TYPE not in json_data \
                    or fields.USER_DEVICE_ID not in json_data:
                raise AuthenticationError('Nie przekazano odpowiednich parametrów.')

            if 'password2' in json_data and json_data[fields.USER_PASSWORD] != json_data['password2']:
                raise AuthenticationError('Podane hasła nie zgadzają się.')

            if len(json_data[fields.USER_PASSWORD]) < 8:
                raise AuthenticationError('Podane hasło jest zbyt krótkie, musi mieć min. 8 znaków.')

            user_doc = await self.findUserByEmail(json_data[fields.USER_EMAIL])
            if user_doc:
                raise AuthenticationError('Podany adres email: {0} jest zajęty.'.format(json_data[fields.USER_EMAIL]))

            user_doc = dict()
            user_doc[fields.USER_TYPE] = UserTypes.EMAIL.value
            user_doc[fields.USER_NAME] = json_data[fields.USER_EMAIL]
            user_doc[fields.USER_EMAIL] = json_data[fields.USER_EMAIL].lower()
            user_doc[fields.USER_DEVICE_TYPE] = json_data[fields.USER_DEVICE_TYPE]
            user_doc[fields.USER_DEVICE_ID] = json_data[fields.USER_DEVICE_ID]

            user_doc[fields.USER_PASSWORD] = self.aes.encrypt(json_data[fields.USER_PASSWORD])
            user_doc[fields.USOS_PAIRED] = False
            user_doc[fields.USER_EMAIL_CONFIRMED] = False
            user_doc[fields.USER_CREATED] = datetime.now()

            user_id = await self.db_insert_user(user_doc)
            self.reset_user_cookie(user_id)

            IOLoop.current().spawn_callback(self.email_confirmation, json_data[fields.USER_EMAIL], user_id)

            self.success(
                'Aby aktywować konto należy kliknąć w link który został Ci wysłany mailem.'.format(
                    self.config.PROJECT_TITLE), cache_age=None)
        except Exception as ex:
            await self.exc(ex)


class EmailLoginHandler(AbstractEmailHandler):
    async def post(self):

        try:
            json_data = escape.json_decode(self.request.body)

            user_doc = await self.findUserByEmail(json_data[fields.USER_EMAIL])

            if not user_doc or user_doc[fields.USER_TYPE] != UserTypes.EMAIL.value or \
                            json_data[fields.USER_PASSWORD] != self.aes.decrypt(
                        user_doc[fields.USER_PASSWORD]).decode():
                raise AuthenticationError('Podano błędne dane do logowania.')

            if not user_doc[fields.USER_EMAIL_CONFIRMED]:
                raise AuthenticationError(
                    'Adres email nie został jeszcze potwierdzony, kliknij na link który Ci wysłaliśmy mailem.')

            token = {
                'token': self.aes.encrypt(str(user_doc[fields.MONGO_ID])).decode(),
                fields.USER_EMAIL: json_data[fields.USER_EMAIL],
                fields.USER_TYPE: user_doc[fields.USER_TYPE],
                fields.USER_ID: user_doc[fields.MONGO_ID],
            }

            await self.db_insert_token(token)
            self.success(data={'token': token['token']})

        except Exception as ex:
            await self.exc(ex)


class EmailConfirmHandler(AuthenticationHandler):
    async def get(self, token):
        try:
            user_id = self.aes.decrypt(token.encode()).decode()
            user_doc = await self.db[collections.USERS].find_one({fields.MONGO_ID: ObjectId(user_id)})

            if not user_doc:
                self.error(message='Błędny parametr wywołania.', code=403)
            elif fields.USER_EMAIL_CONFIRMED in user_doc and user_doc[fields.USER_EMAIL_CONFIRMED]:
                self.error(message='Token wykorzystany. Email potwierdzony.', code=403)
            else:
                user_doc[fields.USOS_PAIRED] = False
                user_doc[fields.USER_EMAIL_CONFIRMED] = True
                user_doc[fields.UPDATE_TIME] = datetime.now()

                await self.db_update_user(user_doc[fields.MONGO_ID], user_doc)
                self.redirect(self.config.DEPLOY_WEB + '/login?token=' + token)
        except Exception as ex:
            await self.exc(ex)
