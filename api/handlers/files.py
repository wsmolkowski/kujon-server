# coding=UTF-8

import logging
import uuid
from datetime import datetime

import pyclamd
from tornado.ioloop import IOLoop
from tornado.web import escape

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections, config
from commons.enumerators import UploadFileStatus, Environment
from commons.errors import FilesError


class AbstractFileHandler(ApiHandler):
    _clamd = None

    def on_finish(self):

        IOLoop.current().spawn_callback(self.db_insert, collections.FILES_DOWNLOADS, {
            fields.USER_ID: self.get_current_user()[fields.MONGO_ID],
            fields.CREATED_TIME: datetime.now(),
            'method': self.request.method,
            'path': self.request.path,
            'query': self.request.query,
            'remote_ip': self.get_remote_ip()
        }, update=False)

    @property
    def clamd(self):
        if not self._clamd:
            self._clamd = pyclamd.ClamdNetworkSocket()
        return self._clamd

    async def _validateFile(self, file_id, file_content):
        try:
            scan_result = self.clamd.scan_stream(file_content)
            if scan_result:
                logging.info('file_id {0} virus found {1}'.format(file_id, scan_result))
                return False

            return True

        except (pyclamd.BufferTooLongError, pyclamd.ConnectionError) as ex:
            logging.debug(ex)
            return False

    async def _storeFile(self, file_id, file_content):

        file_ok = await self._validateFile(file_id, file_content)
        if file_ok:
            file_upload_id = await self.fs.upload_from_stream()
            status = UploadFileStatus.STORED.value
        else:
            status = UploadFileStatus.INVALID.value
            file_upload_id = None

        file_doc = await self.db[collections.FILES].find_one({fields.MONGO_ID: file_id})
        file_doc[fields.FILE_UPLOAD_ID] = file_upload_id
        file_doc[fields.FILE_STATUS] = status
        file_doc[fields.UPDATE_TIME] = datetime.now()

        file_id = await self.db[collections.FILES].update({fields.MONGO_ID: file_id}, file_doc)
        logging.debug('Updated file_id: {0} with status: {1}'.format(file_id, status))

    async def apiGetUserFiles(self):

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.USER_ID: self.getUserId()}
        cursor = self.db[collections.FILES].find(pipeline)
        return await cursor.to_list(None)

    async def apiGetFiles(self, term_id, course_id):

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.COURSE_ID: course_id, fields.TERM_ID: term_id}
        cursor = self.db[collections.FILES].find(pipeline)
        return await cursor.to_list(None)

    async def apiGetFile(self, file_id, remote_address):
        pipeline = {fields.USOS_ID: self.getUsosId(), fields.USER_ID: self.getUserId(),
                    fields.FILE_ID: file_id}
        cursor = self.db[collections.FILES].find(pipeline)
        file_doc = await cursor.to_list(None)

        return file_doc

    async def apiStorefile(self, term_id, course_id, file_name, file_type, file_content):

        file_doc = dict()
        file_doc[fields.USER_ID] = self.getUserId()
        file_doc[fields.USOS_ID] = self.getUsosId()
        file_doc[fields.TERM_ID] = term_id
        file_doc[fields.COURSE_ID] = course_id

        file_doc[fields.FILE_SIZE] = 999
        file_doc[fields.FILE_STATUS] = UploadFileStatus.NEW.value
        file_doc[fields.FILE_TYPE] = file_type
        file_doc[fields.FILE_NAME] = file_name
        file_doc[fields.FILE_ID] = str(uuid.uuid4())

        file_id = await self.db_insert(collections.FILES, file_doc, update=False)
        IOLoop.current().spawn_callback(self._storeFile, file_id, file_content)
        return file_doc[fields.FILE_ID]


class FileHandler(AbstractFileHandler):
    SUPPORTED_METHODS = ('OPTIONS', 'GET', 'DELETE')

    @decorators.authenticated
    async def get(self, file_id):
        try:
            remote_address = self.get_remote_ip()
            if not remote_address:
                if self.config.ENVIRONMENT.lower() in [Environment.DEVELOPMENT.value, Environment.TESTS.value]:
                    remote_address = "127.0.0.1"
                else:
                    logging.error('Bład rozpoznawania adres IP')

            file_doc = await self.apiGetFile(file_id, remote_address)
            if file_doc:
                self.success(file_doc, cache_age=config.SECONDS_YEAR)
            else:
                self.error("Nie znaleziono pliku.", code=404)

        except Exception as ex:
            await self.exc(ex)

    @decorators.authenticated
    async def delete(self, file_id):
        try:
            file_doc = await self.db[collections.FILES].find_one({fields.FILE_ID: file_id,
                                                                  fields.FILE_STATUS: UploadFileStatus.STORED.value,
                                                                  fields.USER_ID: self.getUserId(),
                                                                  fields.USOS_ID: self.getUsosId()})

            if not file_doc:
                self.error("Nie znaleziono pliku.", code=404)
                return

            # await self.fs.delete(file_doc[fields.FILE_UPLOAD_ID])

            file_doc[fields.FILE_STATUS] = UploadFileStatus.DELETED.value

            file_id = await self.db[collections.FILES].update({fields.FILE_ID: file_doc[fields.FILE_ID]}, file_doc)

            self.success(file_id)
        except Exception as ex:
            await self.exc(ex)


class FilesHandler(AbstractFileHandler):
    @decorators.authenticated
    async def get(self, term_id, course_id):
        try:
            files_doc = await self.apiGetFiles(term_id, course_id)
            self.success(files_doc, cache_age=config.SECONDS_HOUR)
        except Exception as ex:
            await self.exc(ex)


class FilesUserHandler(AbstractFileHandler):
    @decorators.authenticated
    async def get(self):
        try:
            files_doc = await self.apiGetUserFiles()
            self.success(files_doc, cache_age=config.SECONDS_HOUR)

        except Exception as ex:
            await self.exc(ex)


class FileUploadHandler(AbstractFileHandler):
    @decorators.authenticated
    async def post(self):
        try:

            fileinfo = self.request.files['filearg'][0]

            json_data = escape.json_decode(self.request.body.decode())

            if fields.TERM_ID not in json_data \
                    or fields.COURSE_ID not in json_data \
                    or fields.FILE_NAME not in json_data \
                    or fields.FILE_CONTENT not in json_data:
                raise FilesError('Nie przekazano odpowiednich parametrów.')

            file_id = await self.apiStorefile(json_data[fields.TERM_ID],
                                              json_data[fields.COURSE_ID],
                                              json_data[fields.FILE_NAME],
                                              'content-type-to-change',
                                              json_data[fields.FILE_CONTENT])
            self.success(file_id)
        except Exception as ex:
            await self.exc(ex)
