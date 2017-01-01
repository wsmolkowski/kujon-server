# coding=UTF-8

import logging
from datetime import datetime

from tornado.ioloop import IOLoop
from tornado.web import escape

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections, config
from commons.enumerators import UploadFileStatus, Environment
from commons.errors import FilesError


class AbstractFileHandler(ApiHandler):

    def on_finish(self):

        IOLoop.current().spawn_callback(self.db_insert, collections.FILES_DOWNLOADS, {
            fields.USER_ID: self.get_current_user()[fields.MONGO_ID],
            fields.CREATED_TIME: datetime.now(),
            'method': self.request.method,
            'path': self.request.path,
            'query': self.request.query,
            'remote_ip': self.get_remote_ip()
        }, update=False)


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
