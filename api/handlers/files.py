# coding=UTF-8

import logging
from datetime import datetime

from tornado.web import escape

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections, config
from commons.enumerators import UploadFileStatus, Environment
from commons.errors import FilesError


class FilesHandlerByID(ApiHandler):
    @decorators.authenticated
    async def get(self, file_id):
        try:
            remote_address = self.request.headers.get("X-Real-IP")
            if not remote_address:
                if self.config.ENVIRONMENT.lower() in [Environment.DEVELOPMENT.value, Environment.TESTS.value]:
                    remote_address = "127.0.0.1"
                else:
                    self.error("Bład rozpoznawania adres IP.", code=200)
                    return

            file_doc = await self.api_get_file_by_id(file_id, remote_address)
            if file_doc:
                self.success(file_doc, cache_age=config.SECONDS_YEAR)
            else:
                self.error("Nie znaleziono pliku.", code=404)

        except Exception as ex:
            await self.exc(ex)


class FilesHandlerByTermIDCourseID(ApiHandler):
    @decorators.authenticated
    async def get(self, term_id, course_id):
        try:
            files_doc = await self.api_files(term_id, course_id)
            self.success(files_doc, cache_age=config.SECONDS_HOUR)
        except Exception as ex:
            await self.exc(ex)


class FilesHandler(ApiHandler):

    @decorators.authenticated
    async def get(self):
        try:
            files_doc = await self.api_files_for_user()
            self.success(files_doc, cache_age=config.SECONDS_HOUR)

        except Exception as ex:
            await self.exc(ex)



    @decorators.authenticated
    async def delete(self, file_id):

        try:
            file_doc = await self.db[collections.FILES].find_one({fields.MONGO_ID: file_id})

            if file_doc[fields.USER_ID] != self.getUserId():
                raise FilesError('Cannot delete another user\'s file.')

            # await self.fs.delete(file_doc[fields.FILE_UPLOAD_ID])
            # logging.debug('deleted file content for: {0}'.format(file_doc[fields.MONGO_ID]))

            file_doc[fields.FILE_STATUS] = UploadFileStatus.DELETED.value
            file_doc[fields.UPDATE_TIME] = datetime.now()

            file_id = await self.db[collections.FILES].update({fields.MONGO_ID: file_id}, file_doc)

            logging.debug('changed file status: {0} to: {1}'.format(file_id, UploadFileStatus.DELETED.value))

            self.success(file_id)
        except Exception as ex:
            await self.exc(ex)


class FilesHandlerUploadV1(ApiHandler):

    @decorators.authenticated
    async def post(self):
        try:
            json_data = escape.json_decode(self.request.body.decode())

            if fields.TERM_ID not in json_data \
                    or fields.COURSE_ID not in json_data \
                    or fields.FILE_NAME not in json_data \
                    or fields.FILE_CONTENT not in json_data:
                raise FilesError('Nie przekazano odpowiednich parametrów.')

            file_id = await self.api_storefile_by_termid_courseid(json_data[fields.TERM_ID],
                                                                  json_data[fields.COURSE_ID],
                                                                  json_data[fields.FILE_NAME],
                                                                  'content-type-to-change',
                                                                  json_data[fields.FILE_CONTENT])
            self.success(file_id)
        except Exception as ex:
            await self.exc(ex)
