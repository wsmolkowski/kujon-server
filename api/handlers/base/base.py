# coding=UTF-8

import logging
import traceback
from datetime import datetime, timedelta

from bson.objectid import ObjectId
from cryptography.fernet import InvalidToken
from tornado import web
from tornado.httpclient import HTTPError

from commons.constants import collections, fields, config
from commons.enumerators import Environment, UserTypes
from commons.enumerators import ExceptionTypes
from commons.errors import ApiError, AuthenticationError, CallerError, FilesError
from commons.errors import DaoError
from commons.handlers import AbstractHandler
from commons.mixins.EmailMixin import EmailMixin
from commons.mixins.JSendMixin import JSendMixin


class BaseHandler(AbstractHandler, EmailMixin):
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

    async def _log_db(self, exception):
        exc_doc = {
            'exception': str(exception)
        }

        if isinstance(exception, HTTPError):
            exc_doc['code'] = exception.code
            exc_doc['message'] = exception.message
            if hasattr(exception, 'response') and hasattr(exception.response, 'body'):
                exc_doc['body'] = str(exception.response.body)
                exc_doc['effective_url'] = exception.response.effective_url

        if self.get_current_user():
            exc_doc[fields.USER_ID] = self.getUserId()

        exc_doc['traceback'] = traceback.format_exc()
        stack = traceback.extract_stack()
        filename, codeline, function_name, text = stack[-2]

        exc_doc['codeline'] = codeline
        exc_doc['function_name'] = function_name
        exc_doc['exception_type'] = self.EXCEPTION_TYPE if hasattr(self,
                                                                   'EXCEPTION_TYPE') else ExceptionTypes.UNKNOWN.value
        exc_doc[fields.CREATED_TIME] = datetime.now()

        if not isinstance(exception, AuthenticationError):
            await self.db_insert(collections.EXCEPTIONS, exc_doc)

    async def _unsubscribeUsos(self):
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

    async def exc(self, exception, finish=True, log_file=True, log_db=True):
        if log_file:
            logging.exception(exception)

        if log_db:
            await self._log_db(exception)

        if finish:
            if isinstance(exception, ApiError) or isinstance(exception, FilesError):
                self.error(message=str(exception), code=500)
            elif isinstance(exception, AuthenticationError):
                self.error(message=str(exception), code=401)
            elif isinstance(exception, CallerError) or isinstance(exception, HTTPError):
                self.usos()
            else:
                self.fail(message='Wystąpił błąd techniczny, pracujemy nad rozwiązaniem.')

    async def db_users_info_by_user_id(self, user_id, usos):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return await self.db[collections.USERS_INFO].find_one({fields.USER_ID: user_id,
                                                               fields.USOS_ID: usos})

    async def db_insert(self, collection, document, update=False):
        create_time = datetime.now()
        if self.getUsosId():
            document[fields.USOS_ID] = self.getUsosId()
        document[fields.CREATED_TIME] = create_time

        if update:
            document[fields.UPDATE_TIME] = create_time

        doc = await self.db[collection].insert(document)
        logging.debug("document {0} inserted into collection: {1}".format(doc, collection))
        return doc

    async def db_remove(self, collection, pipeline, force=False):
        pipeline_remove = pipeline.copy()

        if not force:
            pipeline_remove[fields.CREATED_TIME] = {
                '$lt': datetime.now() - timedelta(seconds=config.SECONDS_REMOVE_ON_REFRESH)}

        result = await self.db[collection].remove(pipeline_remove)
        logging.debug("removed docs from collection {0} with {1}".format(collection, result))
        return result

    async def db_users(self):
        cursor = self.db[collections.USERS].find({fields.USOS_PAIRED: True},
                                                 (fields.MONGO_ID,
                                                  fields.USOS_ID,
                                                  fields.ACCESS_TOKEN_KEY,
                                                  fields.ACCESS_TOKEN_SECRET))

        users = await cursor.to_list(None)
        return users

    async def db_get_archive_user(self, user_id):
        return await self.db[collections.USERS_ARCHIVE].find_one(
            {fields.USER_ID: user_id, fields.USOS_PAIRED: True})

    async def db_find_user(self):
        return await self.db[collections.USERS].find_one({fields.MONGO_ID: self.getUserId()})

    async def db_find_user_by_usos_id(self, user_id, usos_id):
        '''
        :param user_id:
        :param usos_id:
        :return: document from  COLLECTION_USERS
        '''

        if not isinstance(user_id, str):
            user_id = str(user_id)

        user_doc = await self.db[collections.USERS].find_one({
            fields.USOS_USER_ID: user_id,
            fields.USOS_ID: usos_id
        })

        if not user_doc:
            raise DaoError('Nie znaleziono użytkownika {0} dla usos: {1}'.format(user_id, usos_id))

        return user_doc

    async def db_update(self, collection, _id, document):
        updated = await self.db[collection].update({fields.MONGO_ID: _id}, document)
        logging.debug('collection: {0} updated: {1}'.format(collection, updated))
        return updated

    async def db_update_user(self, _id, document):
        return await self.db_update(collections.USERS, _id, document)

    async def db_insert_user(self, document):
        user_doc = await self.db_insert(collections.USERS, document)
        return user_doc

    async def db_insert_token(self, token):
        await self.db[collections.TOKENS].remove(
            {fields.USER_EMAIL: token[fields.USER_EMAIL], fields.USER_TYPE: token[fields.USER_TYPE]})
        return await self.db_insert(collections.TOKENS, token)

    async def db_remove_token(self, email, user_type):
        result = await self.db[collections.TOKENS].remove({
            fields.USER_EMAIL: email, fields.USER_TYPE: user_type})
        logging.debug(
            'removed from collection {0} token for email {1} resulted in {2}'.format(fields.USER_EMAIL, email,
                                                                                     result))

    async def db_find_token(self, email, user_type):
        '''
        finds token by email and updates creation time
        :param email:
        :return: token_doc
        '''

        token_doc = await self.db[collections.TOKENS].find_one(
            {fields.USER_EMAIL: email, fields.USER_TYPE: user_type})
        if token_doc:
            token_doc[fields.CREATED_TIME] = datetime.now()
            await self.db_update(collections.TOKENS, token_doc[fields.MONGO_ID], token_doc)
        return token_doc

    async def db_user_usos_id(self):
        user_doc = await self.db_find_user()
        if user_doc and fields.USOS_USER_ID in user_doc:
            return user_doc[fields.USOS_USER_ID]
        return

    async def db_save_message(self, message, user_id=None, message_type=None, from_whom=None, notification_text=False,
                              notification_result=False):
        if not message_type:
            message_type = 'email'

        if not from_whom:
            from_whom = self.config.PROJECT_TITLE

        if not user_id:
            user_id = self.getUserId()

        msg_doc = await self.db[collections.MESSAGES].insert({
            fields.USER_ID: user_id,
            fields.CREATED_TIME: datetime.now(),
            fields.FIELD_MESSAGE_FROM: from_whom,
            fields.FIELD_MESSAGE_TYPE: message_type,
            fields.FIELD_MESSAGE_TEXT: message,
            fields.ONESIGNAL_NOTIFICATION_TEXT: notification_text,
            fields.ONESIGNAL_NOTIFICATION_RESULT: notification_result,
        })

        logging.debug('user message saved for message_type: {0} with id: {1}'.format(message_type, msg_doc))

        return msg_doc


class UsosesAllApi(BaseHandler):
    @web.asynchronous
    async def get(self):
        try:
            usoses = await self.db_all_usoses(limit_fields=True)
            self.success(usoses, cache_age=config.SECONDS_HOUR)
        except Exception as ex:
            await self.exc(ex)


class UsosesApi(BaseHandler):
    @web.asynchronous
    async def get(self):
        try:
            result = list()
            usoses = await self.db_usoses()
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