# coding=utf-8

# https://github.com/tornadoweb/tornado/blob/master/demos/file_upload/file_uploader.py

import json
import logging
import mimetypes
from functools import partial
from uuid import uuid4

from tornado import gen
from tornado.httputil import HTTPHeaders
from tornado.testing import gen_test

from commons.constants import fields
from tests.api_tests.base import AbstractApplicationTestBase
from tests.base import USER_DOC


class ApiFilesTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiFilesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

        self.file_sample_with_eicar = 'WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo='
        self.file_sample = bytes('to jest przykładowy plik do testów base64', 'utf-8')
        self.file_name_upload = 'sample_post_file.txt'
        self.course_id = '4018-KON317-CLASS'
        self.term_id = '2015L'

    @gen.coroutine
    def multipart_producer(self, boundary, filenames, write):
        boundary_bytes = boundary.encode()

        for filename in filenames:
            filename_bytes = filename.encode()
            write(b'--%s\r\n' % (boundary_bytes,))
            write(b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' %
                  (filename_bytes, filename_bytes))

            mtype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            write(b'Content-Type: %s\r\n' % (mtype.encode(),))
            write(b'\r\n')
            with open(filename, 'rb') as f:
                while True:
                    # 16k at a time.
                    chunk = f.read(16 * 1024)
                    if not chunk:
                        break
                    write(chunk)

                    # Let the IOLoop process its event queue.
                    yield gen.moment

            write(b'\r\n')
            yield gen.moment

        write(b'--%s--\r\n' % (boundary_bytes,))

    @gen.coroutine
    def _prepare_multipart(self, file_name_upload):
        boundary = uuid4().hex
        producer = partial(self.multipart_producer, boundary, [file_name_upload, ])
        headers = HTTPHeaders({
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary
        })
        return headers, producer

    @gen_test(timeout=10)
    def testUserFileEmptyList(self):

        # when
        result = yield self.assertOK(self.get_url('/files'), method='GET')

        # then
        self.assertEquals(0, len(result['data']))

    @gen_test(timeout=10)
    def testDeleteFileFailure(self):

        # assume fake file_id
        delete_uri = '/files/123'

        # when
        result = yield self.assertFail(self.get_url(delete_uri), method='DELETE')

        # then
        self.assertEquals('Nie znaleziono pliku.', result['message'])

    @gen_test(timeout=10)
    def testGetFilesInvalidCourseEdition(self):

        # assume fake course_id and term_id
        get_uri = '/files?course_id=YYY&term_id=XXXX'

        # when
        result = yield self.assertFail(self.get_url(get_uri), method='GET')

        # then
        self.assertEquals('Nie przekazano odpowiednich parametrów.', result['message'])

    @gen_test(timeout=10)
    def testUploadFailure(self):

        # assume missing term_id
        upload_uri = self.get_url('/filesupload?course_id=123&course_id=X&files=Y')

        # when
        result = yield self.assertFail(upload_uri, method='POST', body=self.file_sample)

        # then
        self.assertEquals('Nie przekazano odpowiednich parametrów #1.', result['message'])

    @gen_test(timeout=30)
    def testUploadAndGetFilesApi(self):

        # assume
        upload_uri = '/filesupload?term_id={0}&course_id={1}'.format(self.term_id, self.course_id)
        headers, producer = yield self._prepare_multipart(self.file_name_upload)

        # when
        file_doc = yield self.assertOK(self.get_url(upload_uri), method='POST', headers=headers, body_producer=producer)

        # then
        self.assertEquals('success', file_doc['status'])  # upload ok
        self.assertEquals(self.file_name_upload, file_doc['data'][0][fields.FILE_NAME])

        yield gen.sleep(2)

        # check if file can be retrieved
        files_doc = yield self.assertOK(self.get_url('/files'), method='GET')
        self.assertEquals(1, len(files_doc['data']))

        # check if it is not shared
        self.assertIsNone(files_doc['data'][0][fields.FILE_SHARED_WITH])
        pass

    @gen_test(timeout=15)
    def testUploadFailurewithSameFilename(self):

        # assume upload file with name
        upload_uri = '/filesupload?term_id={0}&course_id={1}'.format(self.term_id, self.course_id)
        headers, producer = yield self._prepare_multipart(self.file_name_upload)
        result = yield self.assertOK(self.get_url(upload_uri), method='POST', headers=headers, body_producer=producer)

        logging.debug("waiting for result: {0}".format(result))

        # when upload second time with same name into same course_id and term_id
        headers2, producer2 = yield self._prepare_multipart(self.file_name_upload)

        # then should no be able to do it
        result = yield self.assertFail(self.get_url(upload_uri), method='POST', headers=headers2,
                                       body_producer=producer2)
        pass

    @gen_test(timeout=15)
    def testShareFileToEveryoneAndRevoke(self):

        # assume upload file
        upload_uri = '/filesupload?term_id={0}&course_id={1}'.format(self.term_id, self.course_id)
        headers, producer = yield self._prepare_multipart(self.file_name_upload)
        result = yield self.assertOK(self.get_url(upload_uri), method='POST', headers=headers, body_producer=producer)

        # when share to all users
        file_doc = result['data'][0]
        yield self.assertOK(self.get_url('/filesshare'),
                            method='POST',
                            body=json.dumps({
                                'file_id': file_doc[fields.FILE_ID],
                                'share_with': '*'
                            }))

        # then it should be shared for all users
        download_uri = '/files/{0}'.format(file_doc[fields.FILE_ID])
        yield self.assertOK(self.get_url(download_uri), method='GET', contentType='text/plain')

        # when revoke sharing
        file_doc = result['data'][0]
        share_uri = '/filesshare'
        yield self.assertOK(self.get_url(share_uri),
                            method='POST',
                            body=json.dumps({
                                'file_id': file_doc[fields.FILE_ID],
                                'share_with': ''
                            }))

        # then sharing should be revoked
        download_uri = '/files'
        result = yield self.assertOK(self.get_url(download_uri), method='GET')
        self.assertEquals(len(result['data'][0][fields.FILE_SHARED_WITH]), 0)

    @gen_test(timeout=20)
    def testShareFileToSelectedUsers(self):

        # assume that file is uploaded
        upload_uri = '/filesupload?term_id={0}&course_id={1}'.format(self.term_id, self.course_id)
        headers, producer = yield self._prepare_multipart(self.file_name_upload)
        result = yield self.assertOK(self.get_url(upload_uri), method='POST', headers=headers, body_producer=producer)

        # when share to selected users
        file_doc = result['data'][0]
        result = yield self.assertOK(self.get_url('/filesshare'),
                                     method='POST',
                                     body=json.dumps({
                                         'file_id': file_doc[fields.FILE_ID],
                                         'share_with': USER_DOC[fields.USOS_USER_ID] + ';'
                                     }))

        # than it should be only shared for selected users
        self.assertEquals(result['data'][0][fields.FILE_SHARED_WITH][0], USER_DOC[fields.USOS_USER_ID])

    @gen_test(timeout=10)
    def testSharedDownloadFileNotForMe(self):
        # assume


        # assume - upload a file
        upload_uri = '/filesupload?term_id={0}&course_id={1}'.format(self.term_id, self.course_id)
        headers, producer = yield self._prepare_multipart(self.file_name_upload)
        response = yield self.assertOK(self.get_url(upload_uri), method='POST', headers=headers, body_producer=producer)

        # when updating in mongo that it is not my file and not shared for me

        # then I shouldn't have right to download it
