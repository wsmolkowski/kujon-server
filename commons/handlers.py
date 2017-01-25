# coding=UTF-8

import logging
import traceback
from datetime import datetime, timedelta

from tornado import web
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop

from commons import utils, usoshelper
from commons.constants import collections, fields, config
from commons.context import Context
from commons.enumerators import ExceptionTypes
from commons.errors import ApiError, AuthenticationError, CallerError, FilesError
from commons.mixins.JSendMixin import JSendMixin


class AbstractHandler(web.RequestHandler, JSendMixin):
    SUPPORTED_METHODS = ('POST', 'OPTIONS', 'GET')

    def options(self, *args, **kwargs):
        pass

    @property
    def db(self):
        return self.application.settings[config.APPLICATION_DB]

    @property
    def config(self):
        return self.application.settings[config.APPLICATION_CONFIG]

    @property
    def aes(self):
        return self.application.settings[config.APPLICATION_AES]

    @property
    def fs(self):
        return self.application.settings[config.APPLICATION_FS]

    def get_remote_ip(self):
        return self.request.headers.get('X-Forwarded-For',
                                        self.request.headers.get('X-Real-Ip', self.request.remote_ip))

    def get_auth_http_client(self):
        return utils.http_client(self.config.PROXY_HOST, self.config.PROXY_PORT)

    async def _prepare_user(self):
        return

    async def _buildContext(self):
        self._context = Context(self.config, remote_ip=self.get_remote_ip(),
                                io_loop=IOLoop.current())

        try:
            self._context.user_doc = await self._prepare_user()
        except Exception as ex:
            await self.exc(ex)
            return

        if self._context.user_doc and fields.USOS_ID in self._context.user_doc:
            usos_id = self._context.user_doc[fields.USOS_ID]  # request authenticated
        else:
            usos_id = self.get_argument('usos_id', default=None)  # request authentication/register

        if usos_id:
            self._context.usos_doc = await self.db_get_usos(usos_id)

        self._context.settings = await self.db_settings(self.getUserId())
        self._context.setUp()

    async def prepare(self):
        await self._buildContext()

    def get_current_user(self):
        if hasattr(self, '_context'):
            return self._context.user_doc

    def getUsosId(self):
        if hasattr(self, '_context') and self._context.usos_doc:
            return self._context.usos_doc[fields.USOS_ID]

    def getUserId(self):
        user_doc = self.get_current_user()
        if user_doc:
            return user_doc[fields.MONGO_ID]

    def reset_user_cookie(self, user_id):
        self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
        encoded = self.aes.encrypt(str(user_id))
        self.set_secure_cookie(self.config.KUJON_SECURE_COOKIE, encoded, domain=self.config.SITE_DOMAIN)

    def isMobileRequest(self):
        if self.request.headers.get(config.MOBILE_X_HEADER_EMAIL, False) \
                and self.request.headers.get(config.MOBILE_X_HEADER_TOKEN, False):
            return True
        return False

    def getUserSettings(self):
        return self._context.settings

    async def usosCall(self, path, arguments=None):
        return await self._context.usosCaller.call(path, arguments)

    async def asyncCall(self, path, arguments=None, base_url=None, lang=True):
        return await self._context.asyncCaller.call_async(path, arguments, base_url, lang)

    def getUsosUserId(self):
        user_doc = self.get_current_user()
        if user_doc:
            return user_doc[fields.USOS_USER_ID]

    async def findUserByEmail(self, email):
        if not isinstance(email, str):
            email = str(email)

        return await self.db[collections.USERS].find_one({fields.USER_EMAIL: email.lower()})

    async def db_get_usos(self, usos_id):
        return await self.db[collections.USOSINSTANCES].find_one({
            'enabled': True, fields.USOS_ID: usos_id
        })

    async def db_settings(self, user_id):
        '''
        returns settings from COLLECTION_SETTINGS if not exists setts default settings
        :param user_id:
        :return:
        '''
        settings = await self.db[collections.SETTINGS].find_one({fields.USER_ID: user_id})
        if not settings:
            await self.db_settings_update(self.getUserId(), fields.EVENT_ENABLE, False)
            await self.db_settings_update(self.getUserId(), fields.GOOGLE_CALLENDAR_ENABLE, False)

            settings = await self.db[collections.SETTINGS].find_one({fields.USER_ID: user_id})

        if fields.USER_ID in settings: del settings[fields.USER_ID]
        if fields.MONGO_ID in settings: del settings[fields.MONGO_ID]
        return settings

    async def db_settings_update(self, user_id, key, value):
        settings = await self.db[collections.SETTINGS].find_one({fields.USER_ID: user_id})
        if not settings:
            return await self.db[collections.SETTINGS].insert({
                fields.USER_ID: user_id,
                key: value
            })

        settings[key] = value
        return await self.db[collections.SETTINGS].update_one({fields.USER_ID: user_id},
                                                              {'$set': {key: value}})

    async def _manipulateUsoses(self, usoses_doc):
        result = []
        for usos in usoses_doc:
            usos[fields.USOS_LOGO] = self.config.DEPLOY_WEB + usos[fields.USOS_LOGO]

            if self.config.ENCRYPT_USOSES_KEYS:
                usos = dict(self.aes.decrypt_usos(usos))

            result.append(usos)
        return result

    async def db_usoses(self, enabled=True):
        cursor = self.db[collections.USOSINSTANCES].find({'enabled': enabled})
        usoses_doc = await cursor.to_list(None)
        return await self._manipulateUsoses(usoses_doc)

    async def db_all_usoses(self, limit_fields=True):
        if limit_fields:
            cursor = self.db[collections.USOSINSTANCES].find(
                {},
                {fields.MONGO_ID: 0, "contact": 1, "enabled": 1, "logo": 1, "name": 1, "phone": 1,
                 "url": 1, "usos_id": 1, "comment": 1, "comment": 1})
        else:
            cursor = self.db[collections.USOSINSTANCES].find()
        usoses_doc = await cursor.to_list(None)
        return await self._manipulateUsoses(usoses_doc)

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

    async def usos_user_info(self, user_id=None):
        '''
        :param user_id:
        :return: parsed usos user info
        '''

        fields = 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'

        if user_id:
            result = await self.usosCall(path='services/users/user',
                                         arguments={'fields': fields, 'user_id': user_id})
        else:
            result = await self.usosCall(path='services/users/user', arguments={'fields': fields})

        if not result:
            raise ApiError('Problem z pobraniem danych z USOS na temat użytkownika.')

        # strip empty values
        if 'homepage_url' in result and result['homepage_url'] == "":
            result['homepage_url'] = None

        if 'student_status' in result:
            result['student_status'] = usoshelper.dict_value_student_status(result['student_status'])

        # change staff_status to dictionary
        result['staff_status'] = usoshelper.dict_value_staff_status(result['staff_status'])

        return result

class DefaultErrorHandler(AbstractHandler):
    @web.asynchronous
    def get(self):
        self.error(message='Strona o podanym adresie nie istnieje.', code=404)
