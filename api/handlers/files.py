# coding=UTF-8

import logging
from datetime import datetime

from tornado.ioloop import IOLoop
from tornado.web import escape

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections
from commons.enumerators import UploadFileStatus
from commons.errors import FilesError


class AbstractFilesHandler(ApiHandler):

    async def api_files(self, pipeline):
        cursor = self.db[collections.FILES].find(pipeline)
        # TODO: convert USER_ID to name
        # TODO: encode file content with base64
        return await cursor.to_list(None)

    async def api_validate_file(self, file_content):
        # base64.b64encode(file_content)
        # TODO: virus scan
        return True

    async def api_files_scan(self, file_id, file_content):

        file_ok = await self.api_validate_file(file_content)
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


class FilesHandler(AbstractFilesHandler):
    @decorators.authenticated
    async def get(self):
        try:
            json_data = escape.json_decode(self.request.body.decode())

            if fields.TERM_ID not in json_data \
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

            if fields.TERM_ID not in json_data \
                    or fields.COURSE_ID not in json_data \
                    or fields.FILE_NAME not in json_data \
                    or fields.FILE_CONTENT not in json_data:
                raise FilesError('Nie przekazano odpowiednich parametrów.')

            # walidacja hederów multipart/form-data
            json_data[fields.USER_ID] = self.getUserId()
            json_data[fields.USOS_ID] = self.getUsosId()
            json_data[fields.FILE_SIZE] = -1
            json_data[fields.FILE_STATUS] = UploadFileStatus.NEW.value
            json_data[fields.FILE_TYPE] = 'type'

            json_data[fields.CREATED_TIME] = datetime.now()
            json_data[fields.UPDATE_TIME] = datetime.now()

            file_id = self.db_insert(collections.FILES, json_data)
            IOLoop.current().spawn_callback(self.api_files_scan(file_id, json_data[fields.FILE_CONTENT]))
            self.success(file_id)
        except Exception as ex:
            await self.exc(ex)


class FileHandler(AbstractFilesHandler):
    SUPPORTED_METHODS = ('DELETE', 'OPTIONS', 'GET')

    @decorators.authenticated
    async def get(self, file_id):
        try:
            file_doc = await self.db[collections.FILES].find_one({fields.MONGO_ID: file_id})
            if fields.FILE_UPLOAD_ID not in file_doc or not file_doc[fields.FILE_UPLOAD_ID]:
                raise FilesError('File not validated yet.')

            grid_out = await self.fs.open_download_stream_by_name(file_doc[fields.FILE_UPLOAD_ID])
            contents = await grid_out.read()
            self.write(contents)

            #TODO: dodać zapisywanie kto i kiedy i z jakiego IP pobrał plik

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

            self.success('file deleted.')
        except Exception as ex:
            await self.exc(ex)
