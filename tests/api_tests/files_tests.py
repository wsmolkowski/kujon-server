# coding=utf-8

import datetime
import json
from random import randint

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
        random_courseedition = randint(0, len(response['data']))
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
    def testUploadInvalidFile(self):
        # filename
        filename = self.generateRandomFilename()

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # post a file with eicar
        file_json = json.dumps({
            fields.TERM_ID: course_id,
            fields.COURSE_ID: term_id,
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_sample_with_eicar,
        })
        file_doc = yield self.assertOK(self.get_url('/filesupload'), method="POST", body=file_json)

        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # get
        get_uri = '/files/' + file_id
        yield self.assertFail(self.get_url(get_uri), method="GET")

    @gen_test(timeout=10)
    def testUploadFileWithInvalidCourseedition(self):
        filename = self.generateRandomFilename()

        # check invalid term_id abd course_id
        file_json = json.dumps({
            fields.TERM_ID: "AAA",
            fields.COURSE_ID: "ZZZ",
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_sample,
        })
        yield self.assertFail(self.get_url('/filesupload'), method="POST", body=file_json)

    @gen_test(timeout=20)
    def testUploadGetListDeleteFile(self):
        # filename
        filename = self.generateRandomFilename()

        # get user sample course edition
        course_id, term_id = yield from self.getRandomCourseEdition()

        # upload a file
        file_json = json.dumps({
            fields.TERM_ID: term_id,
            fields.COURSE_ID: course_id,
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_sample,
        })
        file_doc = yield self.assertOK(self.get_url('/filesupload'), method="POST", body=file_json)

        if file_doc and 'data' in file_doc:
            file_id = file_doc['data']

        # get
        get_uri = '/files/' + file_id
        yield self.assertOK(self.get_url(get_uri), method="DELETE")

        # list files for given course_id and term_id
        get_uri = '/files/{0}/{1}'.format(term_id, course_id)
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
        # TODO: ???

        pass

    @gen_test(timeout=5)
    def testGetFileById(self):

        filename = self.generateRandomFilename()

        # download file that is not in my course_id/term_id
        download_uri = '/files/' + filename
        yield self.assertFail(self.get_url(download_uri))

    @gen_test(timeout=5)
    def testDeleteFileById(self):

        # try to delete not my file
        delete_uri = '/files/' + self.generateRandomFilename()
        yield self.assertFail(self.get_url(delete_uri), method="DELETE")
