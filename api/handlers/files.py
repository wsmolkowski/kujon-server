# coding=UTF-8

import logging
import mimetypes
import sys
import urllib.parse
from datetime import datetime

import pyclamd
from bson.errors import InvalidId
from bson.objectid import ObjectId
from tornado import escape
from tornado.ioloop import IOLoop

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections
from commons.enumerators import UploadFileStatus
from commons.errors import FilesError

USER_FILES_LIMIT_FIELDS = {fields.CREATED_TIME: 1, fields.FILE_NAME: 1, fields.FILE_SIZE: 1,
                           fields.FILE_CONTENT_TYPE: 1, fields.TERM_ID: 1,
                           fields.COURSE_ID: 1, fields.MONGO_ID: 1, fields.USOS_USER_ID: 1,
                           fields.FILE_SHARED_WITH: 1, 'first_name': 1, 'last_name': 1, fields.FILE_SHARED_WITH_IDS: 1}

FILES_LIMIT_FIELDS = {fields.CREATED_TIME: 1, fields.FILE_NAME: 1, fields.FILE_SIZE: 1,
                      fields.FILE_CONTENT_TYPE: 1, fields.TERM_ID: 1,
                      fields.COURSE_ID: 1, fields.MONGO_ID: 1, fields.USOS_USER_ID: 1, fields.FILE_SHARED_WITH: 1,
                      fields.FILE_SHARED_WITH_IDS: 1}

FILE_SCAN_RESULT_OK = 'file_clean'
FILES_SHARE_WITH_SEPARATOR = ';'


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
        user_info = await self.api_user_usos_info()

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.FILE_STATUS: UploadFileStatus.STORED.value,
                    '$or': [{fields.FILE_SHARED_WITH: user_info[fields.ID]},
                            {fields.USER_ID: self.getUserId()}]}

        cursor = self.db[collections.FILES].find(pipeline, USER_FILES_LIMIT_FIELDS)
        files_doc = await cursor.to_list(None)

        # change file id from _id to fields.FILE_ID
        for file in files_doc:
            file[fields.FILE_ID] = file[fields.MONGO_ID]
            file.pop(fields.MONGO_ID)

        return files_doc

    async def apiGetFiles(self, term_id, course_id):

        user_info = await self.api_user_usos_info()

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.COURSE_ID: course_id,
                    fields.TERM_ID: term_id, fields.FILE_STATUS: UploadFileStatus.STORED.value,
                    '$or': [{fields.FILE_SHARED_WITH: user_info[fields.ID]},
                            {fields.FILE_SHARED_WITH: '*'},
                            {fields.USER_ID: ObjectId(self.getUserId())}]}

        cursor = self.db[collections.FILES].find(pipeline, FILES_LIMIT_FIELDS)

        files_doc = await cursor.to_list(None)

        # attach uploading person
        for file_doc in files_doc:
            user_info = await self.api_user_info(file_doc[fields.USOS_USER_ID])
            file_doc['first_name'] = user_info['first_name']
            file_doc['last_name'] = user_info['last_name']

        # change file id from _id to fields.FILE_ID
        for file in files_doc:
            file[fields.FILE_ID] = file[fields.MONGO_ID]
            file.pop(fields.MONGO_ID)

        return files_doc

    async def apiGetFile(self, file_id):
        user_info = await self.api_user_usos_info()

        pipeline = {fields.USOS_ID: self.getUsosId(),
                    fields.MONGO_ID: ObjectId(file_id),
                    fields.FILE_STATUS: UploadFileStatus.STORED.value,
                    '$or': [{fields.FILE_SHARED_WITH: user_info[fields.ID]},
                            {fields.FILE_SHARED_WITH: 'All'},
                            {fields.USER_ID: ObjectId(self.getUserId())}]
                    }

        file_doc = await self.db[collections.FILES].find_one(pipeline)
        if file_doc:
            return file_doc

        raise FilesError('Nie znaleziono pliku.')

    async def apiStoreFile(self, term_id, course_id, file_name, file_content, file_shared_with, file_shared_with_ids):

        # get user info
        file_doc = dict()
        file_doc[fields.USER_ID] = self.getUserId()

        # check if user is on given course_id & term_id
        courseedition = await self.api_course_edition(course_id, term_id)
        if not courseedition:
            raise FilesError('nierozpoznane parametry kursu.')

        # check if such a file exists
        try:
            pipeline = {fields.USOS_ID: self.getUsosId(),
                        fields.TERM_ID: term_id,
                        fields.COURSE_ID: course_id,
                        fields.FILE_NAME: file_name,
                        fields.FILE_STATUS: {'$in': [UploadFileStatus.STORED.value, UploadFileStatus.NEW.value]}}
            exising_file_doc = await self.db[collections.FILES].find_one(pipeline)
            if exising_file_doc:
                raise FilesError('plik o podanej nazwie już istnieje.')
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
        file_doc[fields.FILE_SHARED_WITH] = file_shared_with
        file_doc[fields.FILE_SHARED_WITH_IDS] = file_shared_with_ids

        # rozpoznawanie rodzaju contentu
        try:
            file_doc[fields.FILE_CONTENT_TYPE] = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        except Exception:
            file_doc[fields.FILE_CONTENT_TYPE] = 'application/octet-stream'

        file_id = await self.db_insert(collections.FILES, file_doc, update=False)
        IOLoop.current().spawn_callback(self._storeFile, file_id, file_content)
        return file_id


class FileHandler(AbstractFileHandler):
    SUPPORTED_METHODS = ('OPTIONS', 'GET', 'DELETE')

    @decorators.authenticated
    async def get(self, file_id):
        '''
        :param file_id: file_id do pobrania
        :return:
        '''
        try:
            file_doc = await self.apiGetFile(file_id)

            # check if in my course_edition
            result = await self.api_course_edition(file_doc[fields.COURSE_ID], file_doc[fields.TERM_ID])
            if not result:
                raise FilesError('Nie znaleziono edycji kursu.')

            self.set_header('Content-Type', file_doc[fields.FILE_CONTENT_TYPE])
            self.set_header('Content-Disposition', u'attachment; filename={utf_filename}'.format(utf_filename=urllib.parse.quote(file_doc[fields.FILE_NAME].encode('utf-8'))))
            self.write(file_doc[fields.FILE_CONTENT])
        except FilesError as ex:
            await self.exc(ex, log_db=False, log_file=False)
        except Exception as ex:
            await self.exc(ex)

    @decorators.authenticated
    async def delete(self, file_id):
        '''
        :param file_id: identyfikat pliku do skasowania
        :return:
        '''
        try:
            try:
                file_id = ObjectId(file_id)
            except InvalidId:
                raise FilesError('Błedny identyfikator pliku.')

            pipeline = {fields.MONGO_ID: file_id, fields.FILE_STATUS: UploadFileStatus.STORED.value,
                        fields.USER_ID: self.getUserId(), fields.USOS_ID: self.getUsosId()}
            file_doc = await self.db[collections.FILES].find_one(pipeline)

            if not file_doc:
                raise FilesError('Nie znaleziono pliku.')

            file_update_doc = await self.db[collections.FILES].update({fields.MONGO_ID: ObjectId(file_id)},
                                                                      {'$set': {fields.FILE_STATUS: UploadFileStatus.DELETED.value}})
            if file_update_doc['ok'] != 1:
                raise FilesError('Bład podczas usuwania pliku.')
            else:
                self.success(file_id)

        except FilesError as ex:
            await self.exc(ex, log_db=False, log_file=False)
        except Exception as ex:
            await self.exc(ex)


class FilesHandler(AbstractFileHandler):
    @decorators.authenticated
    async def get(self):
        '''
        :param: course_id
                term_idcours
        :return:
        '''
        try:
            course_id = self.get_argument(fields.COURSE_ID, default=None)
            term_id = self.get_argument(fields.TERM_ID, default=None)

            if course_id and term_id:

                # check if user is on given course_id & term_id
                result = await self.api_course_edition(course_id, term_id)
                if not result:
                    raise FilesError('Nie przekazano odpowiednich parametrów.')

                files_doc = await self.apiGetFiles(term_id, course_id)
            else:
                files_doc = await self.apiGetUserFiles()

            self.success(files_doc, cache_age=0)

        except FilesError as ex:
            await self.exc(ex, log_db=False, log_file=False)
        except Exception as ex:
            await self.exc(ex)


class FilesUploadHandler(AbstractFileHandler):
    @decorators.authenticated
    async def post(self):
        '''
            send params in multipart POST

            'files': [] #lista plików dołaczona multiparem
            'course_id': 'E-1IZ2-1003-s1', # id kursu na które uploadujacy uczeszcza i chce umiescic plik
            'term_id': '2013/14-1' # term_id związane z course_id
            'file_share_with': [] lub '*' lub [123, 4334, 123123, 33]

        :return:
        {
          "code": 200,
          "data": [    #lista plików
            {
              "file_id": "5879b81ef296ff0b4e10a492", #id pliku który wgrywaliśmy
              "file_name": "dodawanie do kujona.png",
              "file_shared_with": []        # pusta lista oznacza żę plik nie jest wyszerowany
            }
          ],
          "status": "success"
        }
        '''
        try:

            course_id = self.get_argument(fields.COURSE_ID, default=None)
            term_id = self.get_argument(fields.TERM_ID, default=None)
            file_shared_with = self.get_argument(fields.FILE_SHARED_WITH, default=None)
            file_shared_with_ids = self.get_argument(fields.FILE_SHARED_WITH_IDS, default=None)
            files = self.request.files

            if not term_id or not course_id or not files or not file_shared_with:  # or 'files' not in files
                raise FilesError('Nie przekazano odpowiednich parametrów.')

            try:
                if file_shared_with == 'List':
                    file_shared_with_ids = file_shared_with_ids.replace(' ', '')
                    file_shared_with_ids = file_shared_with_ids.split(FILES_SHARE_WITH_SEPARATOR)
                    file_shared_with_ids = [x for x in file_shared_with_ids if x != '']
            except Exception:
                raise FilesError('Nie przekazano odpowiednich parametrów sharepowania listy.')

            if file_shared_with not in ['All', 'None', 'List']:
                raise FilesError('Nie przekazano odpowiednich parametrów sharepowania.')

            if file_shared_with in ['All', 'None']:
                file_shared_with_ids = list()


            files_doc = list()
            for key, file in files.items():
                if isinstance(file, list):
                    file = file[0]  # ['files']
                filename = file['filename']
                file_id = await self.apiStoreFile(term_id, course_id, filename, file['body'], file_shared_with, file_shared_with_ids)

                files_doc.append({fields.FILE_ID: file_id,
                                  fields.FILE_NAME: filename,
                                  fields.FILE_SHARED_WITH: file_shared_with,
                                  fields.FILE_SHARED_WITH_IDS: file_shared_with_ids})

            self.success(files_doc)
        except FilesError as ex:
            await self.exc(ex, log_db=False, log_file=False)
        except Exception as ex:
            await self.exc(ex)


class FilesShareHandler(AbstractFileHandler):
    async def apiShareFile(self, file_id, file_shared_with, file_shared_with_ids):

        file_doc = await self.apiGetFile(file_id)

        # check if it is my file
        if file_doc[fields.USER_ID] != self.getUserId():
            raise FilesError('Nie można zmienić uprawnień dla nieswojego pliku.')

        courseedition = await self.api_course_edition(file_doc[fields.COURSE_ID], file_doc[fields.TERM_ID])
        if not courseedition:
            raise FilesError('Błędne parametry kursu.')

        # check if given share_to are in this courseedition
        participant_ids = list()
        if file_shared_with is 'List':
            for participant in courseedition[fields.PARTICIPANTS]:
                participant_ids.append(participant[fields.USER_ID])

            if not set(file_shared_with_ids) <= set(participant_ids):
                raise FilesError('Nie udało się rozpoznać użytkowników.')

        # share
        file_update_doc = await self.db[collections.FILES].update({fields.MONGO_ID: ObjectId(file_id)},
                                                                  {'$set': {
                                                                      fields.FILE_SHARED_WITH: file_shared_with,
                                                                      fields.FILE_SHARED_WITH_IDS: file_shared_with_ids
                                                                  }})
        if file_update_doc['ok'] != 1:
            raise FilesError('Błąd podczas udostępniania pliku.')

    @decorators.authenticated
    async def post(self):
        '''
        :body
            json file
            {
                'file_id': '123', # file_id które się dostaje podczas uploadu
                'share_with': '*' # '*' # '*' oznacza wszystkich użytkowników null nikgo (plik nie wyszerowany) a lista użytkowników do sharpowania [123,1233,48444] gdzie poszczególne numery to id_usera.
            }
        :return: json file
        {
          "code": 200,
          "data": [
            {
              "file_id": "123",
              "file_shared_with": "All" "None" "List"
            }
          ],
          "status": "success"
        }
        '''

        try:
            try:
                args_doc = escape.json_decode(self.request.body)
            except ValueError:
                raise FilesError("Błędne parametry wywołania.")

            result_doc = list()
            for file_doc in args_doc:

                if file_doc[fields.FILE_SHARED_WITH] in ['All', 'None']:
                    file_doc[fields.FILE_SHARED_WITH_IDS] = list()

                await self.apiShareFile(file_doc[fields.FILE_ID], file_doc[fields.FILE_SHARED_WITH], file_doc[fields.FILE_SHARED_WITH_IDS])
                result_doc.append({fields.FILE_ID: file_doc[fields.FILE_ID],
                                   fields.FILE_SHARED_WITH: file_doc[fields.FILE_SHARED_WITH],
                                   fields.FILE_SHARED_WITH_IDS: file_doc[fields.FILE_SHARED_WITH_IDS]})
            self.success(file_doc)

        except FilesError as ex:
            await self.exc(ex, log_db=False, log_file=False)
        except Exception as ex:
            await self.exc(ex)
