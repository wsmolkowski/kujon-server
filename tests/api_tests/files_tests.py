# coding=utf-8

from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.testing import gen_test

from commons.constants import config
from tests.api_tests.base import AbstractApplicationTestBase
from tests.base import USER_DOC, TOKEN_DOC


class ApiFilesTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiFilesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

        self.file_sample_with_eicar = 'WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo='
        self.file_sample = bytes('to jest przykładowy plik do testów base64', 'utf-8')
        self.file_name_upload = 'sample upload file'

    # def getRandomCourseEdition(self):
    #     response = yield self.assertOK(self.get_url('/courseseditions'), method='GET')
    #     random_courseedition = randint(0, len(response['data']) - 1)
    #     term_id = response['data'][random_courseedition][fields.TERM_ID]
    #     course_id = response['data'][random_courseedition][fields.COURSE_ID]
    #     return course_id, term_id

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
            4. list files
        '''

        # assume
        term_id = '2015L'
        course_id = '4018-KON317-CLASS'
        upload_uri = self.get_url(
            '/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, self.file_name_upload))

        headers = HTTPHeaders({
            config.MOBILE_X_HEADER_EMAIL: USER_DOC['email'],
            config.MOBILE_X_HEADER_TOKEN: TOKEN_DOC['token'],
            config.MOBILE_X_HEADER_REFRESH: 'True',
        })

        request = HTTPRequest(url=upload_uri,
                              method='POST',
                              body=self.file_sample,
                              headers=headers,
                              allow_nonstandard_methods=True)

        file_doc = yield self.client.fetch(request=request)

        self.assertIsNotNone(file_doc['data'])  # upload ok

    # @gen_test(timeout=30)
    # def test_getUserFileList(self):
    #
    #     # get empty list
    #     yield self.assertOK(self.get_url('/files'), method='GET')
    #
    #     # upload 2 files
    #     course_id1, term_id1 = yield from self.getRandomCourseEdition()
    #     # TODO: zmienić na uploadowanie multipartem
    #     file1_doc = yield self.assertOK(self.get_url(
    #         '/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id1, course_id1, self.file_name_upload)),
    #                                     method='POST', body=self.file_sample, headers={'Content-Type': 'text/plain'})
    #     if file1_doc and 'data' in file1_doc:
    #         file1_id = file1_doc['data']
    #
    #     course_id2, term_id2 = yield from self.getRandomCourseEdition()
    #     filename2 = self.generateRandomFilename()
    #
    #     # TODO: zmienić na uploadowanie multipartem
    #     file2_doc = yield self.assertOK(self.get_url(
    #         '/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id2, course_id2, filename2)),
    #         method='POST', body=self.file_sample, headers={'Content-Type': 'text/plain'})
    #     if file2_doc and 'data' in file2_doc:
    #         file2_id = file2_doc['data']
    #
    #     # sleeping sec to finish clam
    #     yield gen.sleep(1)
    #
    #     # get list with 2 files
    #     get_uri = '/files'
    #     list = yield self.assertOK(self.get_url(get_uri), method='GET')
    #     self.assertEquals(len(list['data']), 2)

    '''
    @gen_test(timeout=30)
    def testUploadFileWithEicar(self):

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # upload a file with virus
        # TODO: zmienić na uploadowanie multipartem
        file_doc = yield self.assertOK(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, self.file_name_upload)),
                                       method='POST', body=self.file_sample_with_eicar, headers={'Content-Type': 'text/plain'})
        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # get file with virus
        get_uri = '/files/' + file_id
        yield self.assertFail(self.get_url(get_uri), method='GET')

    @gen_test(timeout=10)
    def testUploadFileWithInvalidCourseedition(self):

        term_id = 'XX'
        course_id = 'YY'

        # upload a file with invalid course and term_id
        yield self.assertFail(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, self.file_name_upload)),
                              method='POST', body=self.file_sample, headers={'Content-Type': 'text/plain'})

    @gen_test(timeout=30)
    def testUploadGetListDeleteFile(self):

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # upload
        # TODO: zmienić na uploadowanie multipartem
        file_doc = yield self.assertOK(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, self.file_name_upload)),
                                       method='POST', body=self.file_sample, headers={'Content-Type': 'text/plain'})
        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # sleeping sec to finish clam
        yield gen.sleep(1)

        # get
        get_uri = '/files/' + file_id
        yield self.assertOK(self.get_url(get_uri), method='GET', contentType='text/plain')

        # list files for given course_id and term_id
        get_uri = '/files?term_id={0}&course_id={1}'.format(term_id, course_id)
        files_doc = yield self.assertOK(self.get_url(get_uri), method='GET')
        self.assertEquals(len(files_doc['data']), 1)
        self.assertEquals(files_doc['data'][0][fields.TERM_ID], term_id)
        self.assertEquals(files_doc['data'][0][fields.COURSE_ID], course_id)
        self.assertEquals(files_doc['data'][0][fields.FILE_NAME], self.file_name_upload)
        self.assertIsNone(files_doc['data'][0][fields.FILE_USER_INFO])

        # delete
        delete_uri = '/files/' + file_id
        yield self.assertFail(self.get_url(delete_uri), method='DELETE')

    @gen_test(timeout=5)
    def testGetAndDeleteFileFromNotMyCourseedition(self):

        # insert into mongo random course_id, term_id and file
        file_doc = dict()
        file_doc[fields.USER_ID] = 'xx'
        file_doc[fields.USOS_ID] = 'DEMO'
        file_doc[fields.TERM_ID] = 'XXXX'
        file_doc[fields.COURSE_ID] = 'YYYY'

        file_doc[fields.FILE_SIZE] = 999
        file_doc[fields.FILE_STATUS] = UploadFileStatus.STORED.value
        file_doc[fields.FILE_NAME] = self.file_name_upload
        file_doc[fields.FILE_USER_INFO] = {'user_id': '1015146', 'first name': 'Ewa', 'last_name': 'Datoń-Pawłowicz'}

        config = Config(options.environment)
        client_db = MongoClient(config.MONGODB_URI)[config.MONGODB_NAME]
        file_id = client_db[collections.USERS].insert(file_doc)

        # try to get document by id
        get_uri = '/files/' + str(file_id)
        yield self.assertFail(self.get_url(get_uri), method='GET')

        # try to delete file by id
        delete_uri = '/files/' + str(file_id)
        yield self.assertFail(self.get_url(delete_uri), method='DELETE')
    '''
