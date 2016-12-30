# coding=UTF-8
import logging
import uuid
from datetime import datetime

import pyclamd

from commons.constants import collections, fields
from commons.enumerators import UploadFileStatus
from commons.mixins.DaoMixin import DaoMixin


class ApiMixinFiles(DaoMixin):

    _clamd = None

    @property
    def clamd(self):
        if not self._clamd:
            self._clamd = pyclamd.ClamdNetworkSocket()
        return self._clamd

    async def _validate_file(self, file_id, file_content):
        try:
            scan_result = self.clamd.scan_stream(file_content)
            if scan_result:
                logging.info('file_id {0} virus found {1}'.format(file_id, scan_result))
                return False

            return True

        except (pyclamd.BufferTooLongError, pyclamd.ConnectionError) as ex:
            logging.debug(ex)
            return False

    async def _store_file(self, file_id, file_content):

        file_ok = await self._validate_file(file_id, file_content)
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

    async def api_files_for_user(self):

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.USER_ID: self.getUserId()}
        cursor = self.db[collections.FILES].find(pipeline)
        return await cursor.to_list(None)

    async def api_files(self, term_id, course_id):

        pipeline = {fields.USOS_ID: self.getUsosId(), fields.COURSE_ID: course_id, fields.TERM_ID: term_id}
        cursor = self.db[collections.FILES].find(pipeline)
        return await cursor.to_list(None)

    async def api_get_file_by_id(self, file_id, remote_address):
        pipeline = {fields.USOS_ID: self.getUsosId(), fields.USER_ID: self.getUserId(),
                    fields.FILE_ID: file_id}
        cursor = self.db[collections.FILES].find(pipeline)
        file_doc = await cursor.to_list(None)

        # logging file download
        log_doc = dict()
        log_doc[fields.FILE_ID] = file_id
        log_doc[fields.USER_ID] = self.getUserId()
        log_doc[fields.USOS_ID] = self.getUsosId()
        log_doc[fields.REMOTE_ADDRESS] = remote_address
        log_doc[fields.CREATED_TIME] = datetime.now()
        log_id = await self.db_insert(collections.FILES_DOWNLOADS, log_doc, update=False)
        if not log_id:
            logging.error('Nie udalo sie zalogować pobrania pliku: {0}'.format(file_id))

        return file_doc

    async def api_storefile_by_termid_courseid(self, term_id, course_id, file_name, file_type, file_content):

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
        # IOLoop.current().spawn_callback(self._store_file(file_id, file_content))
        return file_doc[fields.FILE_ID]







