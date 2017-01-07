# coding=utf-8

import mimetypes
from functools import partial
from uuid import uuid4

from tornado import gen, escape
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.testing import gen_test

from pymongo import MongoClient
from commons.enumerators import UploadFileStatus
from commons.config import Config
from commons.constants import config, fields, collections
from tests.api_tests.base import AbstractApplicationTestBase
from tests.base import USER_DOC, TOKEN_DOC


class ApiShareFileTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiShareFileTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

        self.file_sample = bytes('to jest przykładowy plik do testów base64', 'utf-8')
        self.file_name_upload = 'sample_post_file.txt'

    @gen_test(timeout=10)
    def testShareFile(self):

        # assume
        fileId = "asdasdadasdasd"


        # when shareing file
        result = yield self.assertOK(self.get_url('/files'), method='GET')

        # then getting result with id
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
        delete_uri = self.get_url('/filesupload?course_id=123')

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

    @gen_test(timeout=10)
    def testUploadForSelectedUsers(self):

        # assume - upload for selected user not me
        term_id = '2015L'
        course_id = '4018-KON317-CLASS'

        file_doc = dict()
        file_doc[fields.USER_ID] = USER_DOC[fields.USOS_USER_ID]
        file_doc[fields.USOS_ID] = "DEMO"
        file_doc[fields.TERM_ID] = term_id
        file_doc[fields.COURSE_ID] = course_id

        file_doc[fields.FILE_SIZE] = 999
        file_doc[fields.FILE_STATUS] = UploadFileStatus.STORED.value
        file_doc[fields.FILE_NAME] = "samplename"
        file_doc[fields.FILE_USER_USOS] = {"user_usos_id": "123", "first name": "Ewa", "last_name": "Datoń-Pawłowicz"}
        file_doc[fields.FILE_SHARED_TO] = list('414')

        # TODO: nie wiem dlaczego defaultowo przy testowach odpala development
        config = Config("tests")
        client_db = MongoClient(config.MONGODB_URI)[config.MONGODB_NAME]
        file_id = client_db[collections.FILES].insert(file_doc)

        # when try to get document by id
        get_uri = '/files/' + str(file_id)

        # then
        yield self.assertFail(self.get_url(get_uri), method="GET")

        # when try to delete file by id
        delete_uri = '/files/' + str(file_id)
        yield self.assertFail(self.get_url(delete_uri), method="DELETE")


    @gen_test(timeout=10)
    def testDownloadNotForMe(self):

        # assume - insert into mongo not for me with defined shared_user_usos_ids

        # whet get file list

        # then should have right to get ant to download

        pass


    def testUploadwithSameName(self):

        # assume upload file with name

        # when upload second time with same name into same course_id and term_id

        # then should no be able to do it

        pass


