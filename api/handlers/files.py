# coding=UTF-8

import logging
import mimetypes
import sys
from datetime import datetime

import pyclamd
from bson.objectid import ObjectId
from tornado.ioloop import IOLoop

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections
from commons.enumerators import UploadFileStatus
from commons.errors import FilesError

USER_FILES_LIMIT_FIELDS = {fields.CREATED_TIME: 1, fields.FILE_NAME: 1, fields.FILE_SIZE: 1,
                           fields.FILE_CONTENT_TYPE: 1, fields.TERM_ID: 1,
                           fields.COURSE_ID: 1, fields.MONGO_ID: 1, fields.USOS_USER_ID: 1,
                           fields.FILE_SHARED_TO: 1, 'first_name': 1, 'last_name': 1}

FILES_LIMIT_FIELDS = {fields.CREATED_TIME: 1, fields.FILE_NAME: 1, fields.FILE_SIZE: 1,
                      fields.FILE_CONTENT_TYPE: 1, fields.TERM_ID: 1,
                      fields.COURSE_ID: 1, fields.MONGO_ID: 1, fields.USOS_USER_ID: 1}

FILE_SCAN_RESULT_OK = 'file_clean'


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

    async def _scanForViruses(self, file_id, file_content):
        try:
            scan_result = self.clamd.scan_stream(file_content)
            if not scan_result:
                logging.debug('Zeskanowano plik {0} ClamAV ze statusem pozytywnym nowy status: {1}'.format(
                    file_id, UploadFileStatus.STORED.value))
                return UploadFileStatus.STORED.value, FILE_SCAN_RESULT_OK
            else:
                logging.error('Zeskanowano plik {0} ClamAV ze statusem negatywnym nowy status: {1} wynik: {2}'.format(
                    file_id, UploadFileStatus.INVALID.value, scan_result))
                return UploadFileStatus.INVALID.value, scan_result

        except (pyclamd.BufferTooLongError, pyclamd.ConnectionError) as ex:
            logging.debug(ex)
            return UploadFileStatus.INVALID.value, FILE_SCAN_RESULT_OK

    async def _storeFile(self, file_id, file_content):

        file_status, scan_result = await self._scanForViruses(file_id, file_content)

        file_doc = await self.db[collections.FILES].find_one({fields.MONGO_ID: file_id})
        file_doc[fields.FILE_STATUS] = file_status
        file_doc[fields.FILE_SCAN_RESULT] = scan_result
        file_doc[fields.UPDATE_TIME] = datetime.now()
        file_doc[fields.FILE_CONTENT] = file_content

        return await self.db[collections.FILES].update({fields.MONGO_ID: file_id}, file_doc)

    async def apiGetUserFiles(self):
        # TODO: czy to zapytanie jest potrzebne czy skądś można to wyciągnąć?
        user_info = await self.api_user_usos_info()

        pipeline = {fields.USOS_ID: self.getUsosId(),
                    fields.FILE_STATUS: UploadFileStatus.STORED.value,
                    '$or': [{fields.FILE_SHARED_TO: user_info[fields.ID]}, {fields.USER_ID: self.getUserId()}]}

        cursor = self.db[collections.FILES].find(pipeline, USER_FILES_LIMIT_FIELDS)
        files_doc = await cursor.to_list(None)

        # change file id from _id to fields.FILE_ID
        for file in files_doc:
            file[fields.FILE_ID] = file[fields.MONGO_ID]
            file.pop(fields.MONGO_ID)

        return files_doc

    async def apiGetFiles(self, term_id, course_id):
        # TODO: czy to zapytanie jest potrzebne czy skądś można to wyciągnąć?
        user_info = await self.api_user_usos_info()

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.COURSE_ID: course_id,
                    fields.TERM_ID: term_id, fields.FILE_STATUS: UploadFileStatus.STORED.value,
                    '$or': [{fields.FILE_SHARED_TO: user_info[fields.ID]}, {fields.FILE_SHARED_TO: { '$gt': []}}]}

        cursor = self.db[collections.FILES].find(pipeline, FILES_LIMIT_FIELDS)

        # TODO: for each file return if it is my file or public file or private


        files_doc = await cursor.to_list(None)

        # change file id from _id to fields.FILE_ID
        for file in files_doc:
            file[fields.FILE_ID] = file[fields.MONGO_ID]
            file.pop(fields.MONGO_ID)



        return files_doc

    async def apiGetFile(self, file_id):

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.MONGO_ID: ObjectId(file_id)}

        file_doc = await self.db[collections.FILES].find_one(pipeline)
        if not file_doc:
            return False

        # TODO: checking if can download
        # checking if belongs to me
        # checking if on my course_edition
        # check if it is for every one

        return file_doc

    async def apiStorefile(self, term_id, course_id, file_name, file_content, shared_to_user_usos_ids):

        # get user info
        file_doc = dict()
        file_doc[fields.USER_ID] = self.getUserId()

        # check if user is on given course_id & term_id
        try:
            courseedition = await self.api_course_edition(course_id, term_id)
            if not courseedition:
                raise FilesError("nierozpoznane parametry kursu.")
        except Exception as ex:
            raise FilesError(ex)

        # check if such a file exists
        try:
            pipeline = {fields.USOS_ID: self.getUsosId(), fields.TERM_ID: term_id, fields.COURSE_ID: course_id,
                        fields.FILE_NAME: file_name}
            exising_file_doc = await self.db[collections.FILES].find_one(pipeline)
            if exising_file_doc:
                raise FilesError("plik o podanej nazwie już istnieje.")
        except Exception as ex:
            raise FilesError(ex)

        # check if given users_ids are in this courseedition
        try:
            if shared_to_user_usos_ids:
                shared_to_user_usos_ids = shared_to_user_usos_ids.replace(" ", "").split(',')
                participant_ids = list()
                for participant in courseedition[fields.PARTICIPANTS]:
                    participant_ids.append(participant[fields.USER_ID])

                if not set(shared_to_user_usos_ids) <= set(participant_ids):
                    raise FilesError("nierozpoznani użytkownicy.")
        except Exception as ex:
            raise FilesError(ex)

        # dodawanie informacji o użytkowniku
        user_info = await self.api_user_usos_info()
        file_doc[fields.USER_ID] = self.getUserId()
        file_doc[fields.USOS_USER_ID] = user_info[fields.ID]
        file_doc['first_name'] = user_info['first_name']
        file_doc['last_name'] = user_info['last_name']

        file_doc[fields.USOS_ID] = self.getUsosId()
        file_doc[fields.TERM_ID] = term_id
        file_doc[fields.COURSE_ID] = course_id

        # liczenie rozmiaru pliku w MB
        filesize = sys.getsizeof(file_content)
        if filesize > 0:
            filesize = '{0:.2f}'.format((filesize / 1024 / 1024))
        file_doc[fields.FILE_SIZE] = filesize

        file_doc[fields.FILE_STATUS] = UploadFileStatus.NEW.value
        file_doc[fields.FILE_NAME] = file_name

        # dodanie pola komu udostępniay
        file_doc[fields.FILE_SHARED_TO] = shared_to_user_usos_ids

        # rozpoznawanie rodzaju contentu
        try:
            file_doc[fields.FILE_CONTENT_TYPE] = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        except Exception as ex:
            file_doc[fields.FILE_CONTENT_TYPE] = 'application/octet-stream'

        file_id = await self.db_insert(collections.FILES, file_doc, update=False)
        IOLoop.current().spawn_callback(self._storeFile, file_id, file_content)
        return file_id


class FileHandler(AbstractFileHandler):
    SUPPORTED_METHODS = ('OPTIONS', 'GET', 'DELETE')

    @decorators.authenticated
    async def get(self, file_id):
        try:
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
            pipeline = {fields.MONGO_ID: ObjectId(file_id), fields.FILE_STATUS: UploadFileStatus.STORED.value,
                        fields.USER_ID: self.getUserId(), fields.USOS_ID: self.getUsosId()}
            file_doc = await self.db[collections.FILES].find_one(pipeline)

            if not file_doc:
                self.error('Nie znaleziono pliku.', code=404)
                return

            deleted = {fields.FILE_STATUS: UploadFileStatus.DELETED.value}
            result = await self.db[collections.FILES].update({fields.MONGO_ID: ObjectId(file_id)}, deleted)
            if result:
                self.success(file_id)
            else:
                self.error('Bład podczas usuwania pliku.', code=500)
        except Exception as ex:
            await self.exc(ex)


class FilesHandler(AbstractFileHandler):
    @decorators.authenticated
    async def get(self):
        try:
            course_id = self.get_argument(fields.COURSE_ID, default=None)
            term_id = self.get_argument(fields.TERM_ID, default=None)

            if course_id and term_id:

                # check if user is on given course_id & term_id
                try:
                    result = await self.api_course_edition(course_id, term_id)
                    if not result:
                        return self.error('Nie przekazano odpowiednich parametrów.', code=400)
                except Exception as ex:
                    raise FilesError('Błędne parametry wywołania.')

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

            course_id = self.get_argument(fields.COURSE_ID, default=None)
            term_id = self.get_argument(fields.TERM_ID, default=None)
            shared_to_user_usos_ids = self.get_argument(fields.FILE_SHARED_TO, default=list())
            files = self.request.files

            if not term_id or not course_id or not files:  # or 'files' not in files
                return self.error('Nie przekazano odpowiednich parametrów #1.', code=400)

            files_doc = list()
            for key, file in files.items():
                if isinstance(file, list):
                    file = file[0]  # ['files']
                try:
                    file_id = await self.apiStorefile(term_id, course_id, file['filename'], file['body'], )
                except Exception as ex:
                    self.error("Błąd podczas zapisu pliku: {0}".format(ex))
                    return
                files_doc.append({fields.FILE_ID: file_id,
                                  fields.FILE_NAME: file['filename'],
                                  fields.FILE_SHARED_TO: shared_to_user_usos_ids})

            self.success(files_doc)
        except Exception as ex:
            await self.exc(ex)
