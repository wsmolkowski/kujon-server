# coding=utf-8

# https://github.com/tornadoweb/tornado/blob/master/demos/file_upload/file_uploader.py


import mimetypes
from functools import partial
from uuid import uuid4

from tornado import gen, escape
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.testing import gen_test

from commons.constants import config, fields
from tests.api_tests.base import AbstractApplicationTestBase
from tests.base import USER_DOC, TOKEN_DOC


@gen.coroutine
def multipart_producer(boundary, filenames, write):
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


class ApiFilesTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiFilesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

        self.file_sample_with_eicar = 'WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo='
        self.file_sample = bytes('to jest przykładowy plik do testów base64', 'utf-8')
        self.file_name_upload = 'sample_post_file.txt'

    @gen_test(timeout=10)
    def testUserFileEmptyList(self):
        # when
        result = yield self.assertOK(self.get_url('/files'), method='GET')

        # then
        self.assertEquals(0, len(result['data']))

    @gen_test(timeout=10)
    def testDeleteFileFailure(self):
        # assume
        delete_uri = '/files/123'

        # when
        result = yield self.assertFail(self.get_url(delete_uri), method='DELETE')

        # then
        self.assertEquals('Nie znaleziono pliku.', result['message'])


    @gen_test(timeout=10)
    def testGetFilesInvalidCourseEdition(self):
        # assume
        get_uri = '/files?course_id=YYY&term_id=XXXX'

        # when
        result = yield self.assertFail(self.get_url(get_uri), method='GET')

        # then
        self.assertEquals('Nie przekazano odpowiednich parametrów.', result['message'])


    @gen_test(timeout=10)
    def testUploadFailure(self):
        # assume
        delete_uri = self.get_url('/filesupload?course_id=123')  # mising term_id

        # when
        result = yield self.assertFail(delete_uri, method='POST', body=self.file_sample)

        # then
        self.assertEquals('Nie przekazano odpowiednich parametrów.', result['message'])

    @gen_test(timeout=30)
    def testIntegrationFilesApi(self):
        '''
            1. upload file
            2. get file
            3. delete file
            4. list files   - Watch that CLAMD service must be started
        '''

        # assume
        term_id = '2015L'
        course_id = '4018-KON317-CLASS'
        upload_uri = self.get_url(
            '/filesupload?term_id={0}&course_id={1}'.format(term_id, course_id))

        boundary = uuid4().hex
        producer = partial(multipart_producer, boundary, [self.file_name_upload, ])

        headers = HTTPHeaders({
            config.MOBILE_X_HEADER_EMAIL: USER_DOC['email'],
            config.MOBILE_X_HEADER_TOKEN: TOKEN_DOC['token'],
            config.MOBILE_X_HEADER_REFRESH: 'True',
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary
        })

        request = HTTPRequest(url=upload_uri,
                              method='POST',
                              headers=headers,
                              body_producer=producer)

        # when
        response = yield self.client.fetch(request=request)

        # then
        file_doc = escape.json_decode(response.body)
        self.assertEquals('success', file_doc['status'])  # upload ok
        self.assertEquals(self.file_name_upload, file_doc['data'][0][fields.FILE_NAME])

        yield gen.sleep(5)

        # check if file can be retrieved
        result = yield self.assertOK(self.get_url('/files'), method='GET')

        self.assertEquals(1, len(result['data']))

        @gen_test(timeout=30)
        def testUploadForSelectedUsers(self):
            pass



