# coding=UTF-8

import logging

from bson import ObjectId
from cryptography.fernet import InvalidToken
from tornado import web

from commons import constants
from commons.UsosCaller import AsyncCaller
from commons.enumerators import ExceptionTypes, Environment, UserTypes
from commons.errors import AuthenticationError
from commons.handlers import AbstractHandler
from commons.mixins.ApiFriendsMixin import ApiMixinFriends
from commons.mixins.ApiMixin import ApiMixin
from commons.mixins.ApiSearchMixin import ApiMixinSearch
from commons.mixins.ApiTermMixin import ApiTermMixin
from commons.mixins.ApiUserMixin import ApiUserMixin
from commons.mixins.JSendMixin import JSendMixin
from commons.mixins.SocialMixin import SocialMixin


class BaseHandler(AbstractHandler, SocialMixin):
    EXCEPTION_TYPE = ExceptionTypes.DEFAULT.value

    async def _prepare_user(self):
        cookie_encrypted = self.get_secure_cookie(self.config.KUJON_SECURE_COOKIE)
        if cookie_encrypted:
            try:
                cookie_decrypted = self.aes.decrypt(cookie_encrypted).decode()
                user_doc = await self.db[constants.COLLECTION_USERS].find_one(
                    {constants.MONGO_ID: ObjectId(cookie_decrypted)})
                if user_doc:
                    return user_doc
            except InvalidToken as ex:
                logging.exception(ex)
                self.clear_cookie(self.config.KUJON_SECURE_COOKIE)

        header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
        header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

        if header_email and header_token:
            user_doc = await self.db_find_user_email(header_email)

            if not user_doc:
                return

            if user_doc[constants.USER_TYPE].upper() == UserTypes.GOOGLE.value.upper():
                token_exists = await self.db_find_token(header_email)
                if not token_exists:
                    google_token = await self.google_token(header_token)
                    await self.db_insert_token(google_token)
                return user_doc

            elif user_doc[constants.USER_TYPE].upper() == UserTypes.FACEBOOK.value.upper():
                token_exists = await self.db_find_token(header_email)
                if not token_exists:
                    facebook_token = await self.facebook_token(header_token)
                    await self.db_insert_token(facebook_token)
                return user_doc

            elif user_doc[constants.USER_TYPE].upper() == UserTypes.EMAIL.value.upper():
                if self.aes.decrypt(header_token.encode()).decode() == str(user_doc[constants.MONGO_ID]):
                    return user_doc
                else:
                    raise AuthenticationError("Bład weryfikacji tokenu dla: {0}".format(user_doc[constants.USER_TYPE]))
            else:
                raise AuthenticationError('Nieznany typ użytkownika: {0}'.format(user_doc[constants.USER_TYPE]))
        return

    async def prepare(self):
        await super(BaseHandler, self).prepare()

        if 'usos_doc' in self._context:
            # before login
            self._context.base_uri = self._context.usos_doc[constants.USOS_URL]
            self._context.consumer_token = dict(key=self._context.usos_doc[constants.CONSUMER_KEY],
                                                secret=self._context.usos_doc[constants.CONSUMER_SECRET])

            if self.isRegistered():
                # before usos registration
                self._context.access_token = dict(key=self._context.user_doc[constants.ACCESS_TOKEN_KEY],
                                                  secret=self._context.user_doc[constants.ACCESS_TOKEN_SECRET])

    def getUserId(self, return_object_id=True):
        if self.get_current_user():
            if return_object_id:
                return ObjectId(self.get_current_user()[constants.MONGO_ID])
            return self.get_current_user()[constants.MONGO_ID]
        return

    def isRegistered(self):
        if not self._context:
            return False

        if 'user_doc' not in self._context:
            return False

        if not self._context.user_doc:
            return False

        if constants.ACCESS_TOKEN_KEY not in self._context.user_doc and \
                        constants.ACCESS_TOKEN_SECRET not in self._context.user_doc:
            return False

        return True

    def set_default_headers(self):
        super(BaseHandler, self).set_default_headers()

        self.set_header('Access-Control-Allow-Methods', ', '.join(self.SUPPORTED_METHODS))

        if self.isMobileRequest():
            self.set_header("Access-Control-Allow-Origin", "*")
        else:
            # web client access
            self.set_header("Access-Control-Allow-Origin", self.config.DEPLOY_WEB)
            self.set_header("Access-Control-Allow-Credentials", "true")


class ApiHandler(BaseHandler, ApiMixin, ApiMixinFriends, ApiMixinSearch, JSendMixin, ApiUserMixin, ApiTermMixin):
    EXCEPTION_TYPE = ExceptionTypes.API.value

    def do_refresh(self):  # overwrite from DaoMixin
        if self.request.headers.get(constants.MOBILE_X_HEADER_REFRESH, False):
            return True
        if self.config.ENVIRONMENT.lower() == Environment.DEMO.value:
            return True

        return False


class UsosesApi(BaseHandler, JSendMixin):
    @web.asynchronous
    async def get(self):
        usoses = list()
        for usos in self._context.usoses:
            wanted_keys = [constants.USOS_LOGO, constants.USOS_ID, constants.USOS_NAME, constants.USOS_URL]
            usoses.append(dict((k, usos[k]) for k in wanted_keys if k in usos))

        self.success(usoses, cache_age=constants.SECONDS_HOUR)


class ApplicationConfigHandler(BaseHandler, JSendMixin):
    """
        for mobile and www use
    """

    async def usos_works(self):
        try:
            # await AsyncCaller(self._context).call_async(path='services/events/notifier_status')
            await AsyncCaller(self._context).call_async(path='services/courses/classtypes_index')
            return True
        except Exception as ex:
            logging.exception(ex)
            return False

    @web.asynchronous
    async def get(self):

        user = self.get_current_user()
        if user and constants.USOS_PAIRED in user.keys():
            usos_paired = user[constants.USOS_PAIRED]
        else:
            usos_paired = False

        if usos_paired:
            usos_works = await self.usos_works()
        else:
            usos_works = False

        config = {
            'PROJECT_TITLE': self.config.PROJECT_TITLE,
            'API_URL': self.config.DEPLOY_API,
            'USOS_PAIRED': usos_paired,
            'USER_LOGGED': True if user else False,
            'USOS_WORKS': usos_works
        }

        self.success(data=config)
