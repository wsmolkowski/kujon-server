# coding=utf-8

import datetime
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
from random import randint
from tornado import gen
from tornado.testing import gen_test

from commons.constants import fields
from tests.api_tests.base import AbstractApplicationTestBase


class ApiFilesTest(AbstractApplicationTestBase):
    def setUp(self):

        super(ApiFilesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

        self.file_sample_with_eicar = "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo="
        self.file_sample = "to jest przykładowy plik do testów base64"

    def getRandomCourseEdition(self):
        response = yield self.assertOK(self.get_url('/courseseditions'), method="GET")
        random_courseedition = randint(0, len(response['data'])-1)
        term_id = response['data'][random_courseedition][fields.TERM_ID]
        course_id = response['data'][random_courseedition][fields.COURSE_ID]
        return course_id, term_id

    @staticmethod
    def generateRandomFilename():
        # filename
        basename = "sample_upload"
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix])
        return filename

    @gen_test(timeout=30)
    def test_getEmptyUserFileList(self):
        yield self.assertOK(self.get_url('/files'), method="GET")

    @gen_test(timeout=30)
    def testUploadFileWithEicar(self):
        # filename
        filename = self.generateRandomFilename()

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # upload a file with virus
        file_doc = yield self.assertOK(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, filename)),
                                       method="POST", body=self.file_sample_with_eicar, headers={'Content-Type': 'text/plain'})
        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # get file with virus
        get_uri = '/files/' + file_id
        yield self.assertFail(self.get_url(get_uri), method="GET", contentType='text/plain')

    @gen_test(timeout=10)
    def testUploadFileWithInvalidCourseedition(self):
        filename = self.generateRandomFilename()

        term_id = "XX"
        course_id = "YY"

        # upload a file with invalid course and term_id
        yield self.assertFail(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, filename)),
                               method="POST", body=self.file_sample, headers={'Content-Type': 'text/plain'})

    @gen_test(timeout=30)
    def testUploadGetListDeleteFile(self):
        # filename
        filename = self.generateRandomFilename()

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # upload
        file_doc = yield self.assertOK(self.get_url('/filesupload?term_id={0}&course_id={1}&file_name={2}'.format(term_id, course_id, filename)),
                                       method="POST", body=self.file_sample, headers={'Content-Type': 'text/plain'})
        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # sleeping 3 sec to finish clam
        yield gen.sleep(3)

        # get
        get_uri = '/files/' + file_id
        yield self.assertOK(self.get_url(get_uri), method="GET", contentType='text/plain')

        # list files for given course_id and term_id
        get_uri = '/files?term_id={0}&course_id={1}'.format(term_id, course_id)
        files_doc = yield self.assertOK(self.get_url(get_uri), method="GET")
        self.assertEquals(len(files_doc['data']), 1)
        self.assertEquals(files_doc['data'][0][fields.TERM_ID], term_id)
        self.assertEquals(files_doc['data'][0][fields.COURSE_ID], course_id)
        self.assertEquals(files_doc['data'][0][fields.FILE_NAME], filename)

        # delete
        delete_uri = '/files/' + file_id
        yield self.assertFail(self.get_url(delete_uri), method="DELETE")

    @gen_test(timeout=5)
    def testGetAndDeleteFileFromNotMyCourseedition(self):

        # switch to another user
        # TODO: insert into mongo, try to get
        #

        pass

    @gen_test(timeout=5)
    def testDeleteFileById(self):

        # try to delete not my file
        delete_uri = '/files/' + self.generateRandomFilename()
        yield self.assertFail(self.get_url(delete_uri), method="DELETE")
