# coding=utf-8

import datetime
from random import randint
from tornado import gen
from tornado.testing import gen_test
from tornado.options import options
from pymongo import MongoClient
from commons.constants import fields, collections
from commons.enumerators import UploadFileStatus
from commons.config import Config
from tests.api_tests.base import AbstractApplicationTestBase


class ApiFilesTest(AbstractApplicationTestBase):
    def setUp(self):

        super(ApiFilesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

        self.file_sample_with_eicar = "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo="
        self.file_sample = "to jest przykładowy plik do testów base64"
        self.randomfilename = self.generateRandomFilename()

    def getRandomCourseEdition(self):
        response = yield self.assertOK(self.get_url('/courseseditions'), method="GET")
        random_courseedition = randint(0, len(response['data'])-1)
        term_id = response['data'][random_courseedition][fields.TERM_ID]
        course_id = response['data'][random_courseedition][fields.COURSE_ID]
        return course_id, term_id

    @staticmethod
    def generateRandomFilename():
        # generate sample filename
        basename = "sample_upload"
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix])
        return filename

    @gen_test(timeout=30)
    def test_getUserFileList(self):

        # get empty list
        yield self.assertOK(self.get_url('/files'), method="GET")

        # upload 2 files
        course_id1, term_id1 = yield from self.getRandomCourseEdition()
        # TODO: zmienić na uploadowanie multipartem
        file1_doc = yield self.assertOK(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id1, course_id1, self.randomfilename)),
                                       method="POST", body=self.file_sample, headers={'Content-Type': 'text/plain'})
        if file1_doc and 'data' in file1_doc:
            file1_id = file1_doc['data']

        course_id2, term_id2 = yield from self.getRandomCourseEdition()
        filename2 = self.generateRandomFilename()

        # TODO: zmienić na uploadowanie multipartem
        file2_doc = yield self.assertOK(self.get_url(
            '/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id2, course_id2, filename2)),
                                       method="POST", body=self.file_sample, headers={'Content-Type': 'text/plain'})
        if file2_doc and 'data' in file2_doc:
            file2_id = file2_doc['data']

        # sleeping sec to finish clam
        yield gen.sleep(1)

        # get list with 2 files
        get_uri = '/files'
        list = yield self.assertOK(self.get_url(get_uri), method="GET")
        self.assertEquals(len(list['data']), 2)

        return

    @gen_test(timeout=30)
    def testUploadFileWithEicar(self):

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # upload a file with virus
        # TODO: zmienić na uploadowanie multipartem
        file_doc = yield self.assertOK(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, self.randomfilename)),
                                       method="POST", body=self.file_sample_with_eicar, headers={'Content-Type': 'text/plain'})
        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # get file with virus
        get_uri = '/files/' + file_id
        yield self.assertFail(self.get_url(get_uri), method="GET")

    @gen_test(timeout=10)
    def testUploadFileWithInvalidCourseedition(self):

        term_id = "XX"
        course_id = "YY"

        # upload a file with invalid course and term_id
        yield self.assertFail(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, self.randomfilename)),
                               method="POST", body=self.file_sample, headers={'Content-Type': 'text/plain'})

    @gen_test(timeout=30)
    def testUploadGetListDeleteFile(self):

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # upload
        # TODO: zmienić na uploadowanie multipartem
        file_doc = yield self.assertOK(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, self.randomfilename)),
                                       method="POST", body=self.file_sample, headers={'Content-Type': 'text/plain'})
        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # sleeping sec to finish clam
        yield gen.sleep(1)

        # get
        get_uri = '/files/' + file_id
        yield self.assertOK(self.get_url(get_uri), method="GET", contentType='text/plain')

        # list files for given course_id and term_id
        get_uri = '/files?term_id={0}&course_id={1}'.format(term_id, course_id)
        files_doc = yield self.assertOK(self.get_url(get_uri), method="GET")
        self.assertEquals(len(files_doc['data']), 1)
        self.assertEquals(files_doc['data'][0][fields.TERM_ID], term_id)
        self.assertEquals(files_doc['data'][0][fields.COURSE_ID], course_id)
        self.assertEquals(files_doc['data'][0][fields.FILE_NAME], self.randomfilename)
        self.assertIsNone(files_doc['data'][0][fields.FILE_USER_INFO])

        # delete
        delete_uri = '/files/' + file_id
        yield self.assertFail(self.get_url(delete_uri), method="DELETE")

    @gen_test(timeout=5)
    def testGetAndDeleteFileFromNotMyCourseedition(self):

        # insert into mongo random course_id, term_id and file
        file_doc = dict()
        file_doc[fields.USER_ID] = "xx"
        file_doc[fields.USOS_ID] = "DEMO"
        file_doc[fields.TERM_ID] = "XXXX"
        file_doc[fields.COURSE_ID] = "YYYY"

        file_doc[fields.FILE_SIZE] = 999
        file_doc[fields.FILE_STATUS] = UploadFileStatus.STORED.value
        file_doc[fields.FILE_NAME] = self.randomfilename
        file_doc[fields.FILE_USER_INFO] = {"user_id": "1015146", "first name": "Ewa", "last_name": "Datoń-Pawłowicz"}

        config = Config(options.environment)
        client_db = MongoClient(config.MONGODB_URI)[config.MONGODB_NAME]
        file_id = client_db[collections.USERS].insert(file_doc)

        # try to get document by id
        get_uri = '/files/' + str(file_id)
        yield self.assertFail(self.get_url(get_uri), method="GET")

        # try to delete file by id
        delete_uri = '/files/' + str(file_id)
        yield self.assertFail(self.get_url(delete_uri), method="DELETE")

    @gen_test(timeout=5)
    def testDeleteFileById(self):

        # try to delete not my file
        delete_uri = '/files/' + self.generateRandomFilename()
        yield self.assertFail(self.get_url(delete_uri), method="DELETE")
