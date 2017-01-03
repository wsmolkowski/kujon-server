# coding=UTF-8

import logging
import pyclamd
import gridfs
import mimetypes
from bson.objectid import ObjectId
from datetime import datetime
from tornado.ioloop import IOLoop

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections
from commons.enumerators import UploadFileStatus, Environment
from commons.errors import FilesError

FILES_LIMIT_FIELDS = {'created_time': 1, 'file_name': 1, 'file_size': 1, 'file_content_type': 1, fields.TERM_ID: 1,
                     fields.COURSE_ID: 1, fields.MONGO_ID: 1}


class AbstractFileHandler(ApiHandler):
    _clamd = None

    def on_finish(self):

        IOLoop.current().spawn_callback(self.db_insert, collections.FILES_HISTORY, {
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

            return True
            # TODO do sprawdzenia bo zrobieniu uploadu
            scan_result = self.clamd.scan_stream(file_content)
            if scan_result:
                logging.info('file_id {0} virus found {1}'.format(file_id, scan_result))
                return False


        except (pyclamd.BufferTooLongError, pyclamd.ConnectionError) as ex:
            logging.debug(ex)
            return False

    async def _storeFile(self, file_id, file_content):

        file_ok = await self._validateFile(file_id, file_content)

        if file_ok:
            logging.error("Zeskanowano plik {0} ClamAV ze statusem pozytywnym nowy status: {1}".format(file_id, UploadFileStatus.STORED.value))
            status = UploadFileStatus.STORED.value
        else:
            logging.error("Zeskanowano plik {0} ClamAV ze statusem negatywnym nowy status: {1}".format(file_id, UploadFileStatus.INVALID.value))
            status = UploadFileStatus.INVALID.value

        file_doc = await self.db[collections.FILES].find_one({fields.MONGO_ID: file_id})
        file_doc[fields.FILE_STATUS] = status
        file_doc[fields.UPDATE_TIME] = datetime.now()
        file_doc[fields.FILE_CONTENT] = file_content
        file_id = await self.db[collections.FILES].update({fields.MONGO_ID: file_id}, file_doc)


    async def apiGetUserFiles(self):

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.USER_ID: self.getUserId()}
        cursor = self.db[collections.FILES].find(pipeline, FILES_LIMIT_FIELDS)
        files_doc = await cursor.to_list(None)

        # change file id from _id to fields.FILE_ID
        for file in files_doc:
            file[fields.FILE_ID] = file[fields.MONGO_ID]
            file.pop(fields.MONGO_ID)

        return files_doc

    async def apiGetFiles(self, term_id, course_id):

        # check if user is on given course_id & term_id
        if not await self.api_course_edition(course_id, term_id):
            return None

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.COURSE_ID: course_id, fields.TERM_ID: term_id}
        cursor = self.db[collections.FILES].find(pipeline)
        return await cursor.to_list(None)

    async def apiGetFile(self, file_id):
        pipeline = {fields.USOS_ID: self.getUsosId(), fields.MONGO_ID: ObjectId(file_id)}
        return await self.db[collections.FILES].find_one(pipeline)

    async def apiGetFileContent(self, file_id):
        # todo get file from grifs
        grid_fs = gridfs.GridFS(self.db, collections=collections.FILES_CONTENT)
        return self.fs.get(file_id).read()

    async def apiStorefile(self, term_id, course_id, file_name, file_content):

        # check if user is on given course_id & term_id
        if not await self.api_course_edition(course_id, term_id):
            return None

        file_doc = dict()
        file_doc[fields.USER_ID] = self.getUserId()
        file_doc[fields.USOS_ID] = self.getUsosId()
        file_doc[fields.TERM_ID] = term_id
        file_doc[fields.COURSE_ID] = course_id

        # TODO liczenie rozmiaru pliku
        file_doc[fields.FILE_SIZE] = 999
        file_doc[fields.FILE_STATUS] = UploadFileStatus.NEW.value
        file_doc[fields.FILE_NAME] = file_name

        # TODO: rozpoznawanie contentu i co jak nie rozpozna
        # mime = mimetypes.MimeTypes()
        # file_doc[fields.FILE_CONTENT] = mime.guess_type(file_content)
        file_doc[fields.FILE_CONTENT_TYPE] = "text/plain"

        # TODO - sprawdzic czy ten upload działa asynchronicznie
        # file_upload_id = await self.fs.upload_from_stream()

        file_id = await self.db_insert(collections.FILES, file_doc, update=False)
        IOLoop.current().spawn_callback(self._storeFile, file_id, file_content)
        return file_id


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

            file_doc = await self.apiGetFile(file_id)
            if file_doc:
                self.set_header('Content-Type', file_doc[fields.FILE_CONTENT_TYPE])
                self.write(file_doc[fields.FILE_CONTENT])
            else:
                self.error('Nie znaleziono pliku.', code=404)

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
    async def get(self):
        try:
            course_id = self.get_argument('course_id', default=None)
            term_id = self.get_argument('term_id', default=None)

            if course_id and term_id:
                files_doc = await self.apiGetFiles(term_id, course_id)
            else:
                files_doc = await self.apiGetUserFiles()

            self.success(files_doc, cache_age=0)

        except Exception as ex:
            await self.exc(ex)


class FileUploadHandler(AbstractFileHandler):
    @decorators.authenticated
    async def post(self):
        try:

            course_id = self.get_argument('course_id', default=None)
            term_id = self.get_argument('term_id', default=None)
            files = self.request.files
            if not term_id or not course_id or not files or 'files' not in files:
                return self.error('Nie przekazano odpowiednich parametrów.', code=400)

            files_doc = list()
            for file in files['files']:
                file_id = await self.apiStorefile(term_id, course_id, file['filename'], file['body'])
                files_doc.append(file_id)
            if len(files_doc) > 0:
                self.success(files_doc)
            else:
                self.error("Niepoprawne parametry wywołania 2.", code=400)
        except Exception as ex:
            await self.exc(ex)
