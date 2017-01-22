# coding=UTF-8

import logging

from bson import ObjectId
from cryptography.fernet import InvalidToken
from tornado import web

from commons.constants import fields, collections, config
from commons.enumerators import ExceptionTypes, Environment, UserTypes
from commons.errors import AuthenticationError
from commons.handlers import AbstractHandler
from commons.mixins.ApiMixin import ApiMixin
from commons.mixins.ApiSearchMixin import ApiMixinSearch
from commons.mixins.ApiTermMixin import ApiTermMixin
from commons.mixins.ApiUserMixin import ApiUserMixin
from commons.mixins.JSendMixin import JSendMixin


class BaseHandler(AbstractHandler):
    EXCEPTION_TYPE = ExceptionTypes.DEFAULT.value

    async def _prepare_user(self):
        cookie_encrypted = self.get_secure_cookie(self.config.KUJON_SECURE_COOKIE)
        if cookie_encrypted:
            try:
                cookie_decrypted = self.aes.decrypt(cookie_encrypted).decode()
                user_doc = await self.db[collections.USERS].find_one(
                    {fields.MONGO_ID: ObjectId(cookie_decrypted)})
                if user_doc:
                    return user_doc
            except InvalidToken as ex:
                logging.exception(ex)
                self.clear_cookie(self.config.KUJON_SECURE_COOKIE)

        header_email = self.request.headers.get(config.MOBILE_X_HEADER_EMAIL, False)
        header_token = self.request.headers.get(config.MOBILE_X_HEADER_TOKEN, False)

        if header_email and header_token:
            user_doc = await self.findUserByEmail(header_email)

            if not user_doc or fields.USER_TYPE not in user_doc:
                return

            if user_doc[fields.USER_TYPE].upper() == UserTypes.GOOGLE.value:
                token_exists = await self.db_find_token(header_email, UserTypes.GOOGLE.value)
                if not token_exists:
                    google_token = await self._context.socialCaller.google_token(header_token)
                    google_token[fields.USER_TYPE] = UserTypes.GOOGLE.value
                    await self.db_insert_token(google_token)
                return user_doc

            elif user_doc[fields.USER_TYPE].upper() == UserTypes.FACEBOOK.value:
                token_exists = await self.db_find_token(header_email, UserTypes.FACEBOOK.value)
                if not token_exists:
                    facebook_token = await self._context.socialCaller.facebook_token(header_token)
                    facebook_token[fields.USER_TYPE] = UserTypes.FACEBOOK.value
                    await self.db_insert_token(facebook_token)
                return user_doc

            elif user_doc[fields.USER_TYPE].upper() == UserTypes.EMAIL.value:
                token_exists = await self.db_find_token(header_email, UserTypes.EMAIL.value)
                if not token_exists:
                    raise AuthenticationError(
                        "Token wygasł dla: {0} oraz typu użytkownika {1}. Prośba o zalogowanie.".format(
                            header_email, user_doc[fields.USER_TYPE]))

                try:
                    decrypted_token = self.aes.decrypt(header_token.encode()).decode()
                except InvalidToken:
                    raise AuthenticationError(
                        "Bład weryfikacji tokenu dla: {0} oraz typu użytkownika {1}".format(
                            header_email, user_doc[fields.USER_TYPE]))

                if decrypted_token == str(user_doc[fields.MONGO_ID]):
                    return user_doc
                else:
                    raise AuthenticationError(
                        "Bład weryfikacji tokenu dla: {0} oraz typu użytkownika {1}".format(
                            header_email, user_doc[fields.USER_TYPE]))
            else:
                raise AuthenticationError('Nieznany typ użytkownika: {0}'.format(user_doc[fields.USER_TYPE]))
        return

    def isRegistered(self):
        if not self._context:
            return False

        if self._context.user_doc:
            return False

        if not self._context.user_doc:
            return False

        if fields.ACCESS_TOKEN_KEY not in self._context.user_doc and \
                        fields.ACCESS_TOKEN_SECRET not in self._context.user_doc:
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

    async def _usosWorks(self):
        try:
            # await AsyncCaller(self._context).call_async(path='services/events/notifier_status')
            await self.asyncCall(path='services/courses/classtypes_index')
            return True
        except Exception as ex:
            logging.warning(ex)
            return False

    async def doRefresh(self):
        if self.request.headers.get(config.MOBILE_X_HEADER_REFRESH, False):
            return await self._usosWorks()
        if self.config.ENVIRONMENT.lower() == Environment.DEMO.value:
            return True

        return False


class ApiHandler(BaseHandler, ApiMixin, ApiMixinSearch, JSendMixin, ApiUserMixin, ApiTermMixin):
    EXCEPTION_TYPE = ExceptionTypes.API.value

    async def _unsubscribe_usos(self):
        try:
            current_subscriptions = await self.usosCall(path='services/events/subscriptions')
        except Exception as ex:
            logging.exception(ex)
            current_subscriptions = None

        if current_subscriptions:
            try:
                await self.usosCall(path='services/events/unsubscribe')
                await self.db_remove(collections.SUBSCRIPTIONS, {fields.USER_ID: self.getUserId()})
            except Exception as ex:
                logging.warning(ex)

class UsosesAllApi(BaseHandler, JSendMixin):
    @web.asynchronous
    async def get(self):
        try:
            usoses = await self.db_all_usoses(limit_fields=True)
            self.success(usoses, cache_age=config.SECONDS_HOUR)
        except Exception as ex:
            await self.exc(ex)


class UsosesApi(BaseHandler, JSendMixin):
    @web.asynchronous
    async def get(self):
        try:
            result = list()
            usoses = await self.get_usos_instances()
            for usos in usoses:
                wanted_keys = [fields.USOS_LOGO, fields.USOS_ID, fields.USOS_NAME, fields.USOS_URL]
                result.append(dict((k, usos[k]) for k in wanted_keys if k in usos))

            self.success(result, cache_age=config.SECONDS_HOUR)
        except Exception as ex:
            await self.exc(ex)


class ApplicationConfigHandler(BaseHandler, JSendMixin):
    """
        for mobile and www use
    """

    @web.asynchronous
    async def get(self):
        usos_works = False
        usos_paired = False

        try:
            user = self.get_current_user()
            if user and fields.USOS_PAIRED in user.keys():
                usos_paired = user[fields.USOS_PAIRED]

            if usos_paired:
                usos_works = await self._usosWorks()

            config = {
                'PROJECT_TITLE': self.config.PROJECT_TITLE,
                'API_URL': self.config.DEPLOY_API,
                'USOS_PAIRED': usos_paired,
                'USER_LOGGED': True if user else False,
                'USOS_WORKS': usos_works
            }

            self.success(data=config)

        except Exception as ex:
            logging.exception(ex)
            config = {
                'PROJECT_TITLE': self.config.PROJECT_TITLE,
                'API_URL': self.config.DEPLOY_API,
                'USOS_PAIRED': usos_paired,
                'USER_LOGGED': False,
                'USOS_WORKS': usos_works
            }
            self.success(data=config)
