# coding=UTF-8

import base64
import logging
from datetime import datetime

from tornado.ioloop import IOLoop
from tornado.web import escape
import pyclamd

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections
from commons.enumerators import UploadFileStatus, Environment
from commons.errors import FilesError


class AbstractFilesHandler(ApiHandler):
    async def api_files(self, pipeline):
        cursor = self.db[collections.FILES].find(pipeline)
        # TODO: convert USER_ID to name
        return await cursor.to_list(None)

    async def api_files_scan(self, file_id, file_content):
        if self.config.ENVIRONMENT in (Environment.DEVELOPMENT, ):
            status = UploadFileStatus.STORED
        else:
            # UploadFileStatus.DELETED
            file_content = file_content #TODO: virus scan
            status = UploadFileStatus.STORED

        file_doc = await self.db[collections.FILES].find_one({fields.MONGO_ID: file_id})
        file_doc[fields.FILE_STATUS] = status
        file_doc[fields.FILE_CONTENT] = file_content    # base64.b64encode(json_data[fields.FILE_CONTENT])
        file_doc[fields.UPDATE_TIME] = datetime.now()

        file_id = await self.db[collections.FILES].update({fields.MONGO_ID: file_id}, file_doc)
        logging.debug('Updated file_id: {0} with status: {1}'.format(file_id, status))


class FilesHandler(AbstractFilesHandler):
    @decorators.authenticated
    async def get(self):
        try:
            json_data = escape.json_decode(self.request.body.decode())

            if fields.FILE_ID in json_data:
                file_doc = await self.db[collections.FILES].find_one(
                    {fields.MONGO_ID: json_data[fields.FILE_ID]})
                self.success(file_doc)
                return

            if fields.PROGRAMME_ID not in json_data \
                    or fields.TERM_ID not in json_data \
                    or fields.COURSE_ID not in json_data:
                raise FilesError('Nie przekazano odpowiednich parametrów.')

            json_data[fields.USOS_ID] = self.getUsosId()

            files = await self.api_files(json_data)
            self.success(files)
        except Exception as ex:
            await self.exc(ex)

    @decorators.authenticated
    async def post(self):
        try:
            json_data = escape.json_decode(self.request.body.decode())

            if fields.PROGRAMME_ID not in json_data \
                    or fields.TERM_ID not in json_data \
                    or fields.COURSE_ID not in json_data \
                    or fields.FILE_NAME not in json_data \
                    or fields.FILE_CONTENT not in json_data:
                raise FilesError('Nie przekazano odpowiednich parametrów.')

            # walidacja hederów multipart/form-data
            json_data[fields.USER_ID] = self.getUserId()
            json_data[fields.USOS_ID] = self.getUsosId()
            json_data[fields.FILE_SIZE] = -1
            json_data[fields.FILE_STATUS] = UploadFileStatus.NEW
            json_data[fields.FILE_TYPE] = 'type'

            json_data[fields.CREATED_TIME] = datetime.now()
            json_data[fields.UPDATE_TIME] = datetime.now()

            file_id = self.db_insert(collections.FILES, json_data)
            IOLoop.current().spawn_callback(self.api_files_scan(file_id, json_data[fields.FILE_CONTENT]))
            self.success(file_id)
        except Exception as ex:
            await self.exc(ex)
