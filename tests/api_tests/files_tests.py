# coding=utf-8

import base64
import datetime
import json

from tornado import escape
from tornado.testing import gen_test

from commons.constants import fields
from tests.api_tests.base import AbstractApplicationTestBase


class ApiFilesTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiFilesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

        self.file_based64_with_eicar_encoded = "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo="
        self.file_based64_encoded = "dG8gamVzdCBwcnp5ayYjMzIyO2Fkb3d5IHBsaWsgZG8gdGVzdPN3IGJhc2U2NA=="
        self.file_based64_decoded = "to jest przykładowy plik do testów base64"

    @staticmethod
    def generate_filename():
        # filename
        basename = "sample_upload"
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix])
        return filename

    @gen_test(timeout=30)
    def test_post_file_and_get_file_and_delete(self):

        # filename
        filename = self.generate_filename()

        # get user sample course edition
        response = yield self.fetch_assert(self.get_url('/courseseditions'))
        json_body = escape.json_decode(response.body)
        term_id = json_body['data'][0][fields.TERM_ID]
        course_id = json_body['data'][0][fields.COURSE_ID]

        # upload a file
        file_json = json.dumps({
            fields.TERM_ID: term_id,
            fields.COURSE_ID: course_id,
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_based64_encoded,
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response(response)
        file_upload_id = response[fields.FILE_UPLOAD_ID]

        # download decode and check
        download_uri = '/files/' + file_upload_id
        response = yield self.http_client.fetch(self.get_url(download_uri), method="GET")
        self.assert_api_response(response)
        json_body = escape.json_decode(response.body)
        file_decoded = base64.b64decode(json_body[fields.FILE_CONTENT])
        self.asserEquals(self.file_based64_encoded, file_decoded)
        self.asserEquals(json_body['data'][fields.FILE_NAME], filename)
        self.asserEquals(json_body['data'][fields.COURSE_ID], course_id)
        self.asserEquals(json_body['data'][fields.TERM_ID], term_id)

        # delete file
        delete_uri = '/files/' + json_body[fields.FILE_UPLOAD_ID]
        response = yield self.http_client.fetch(self.get_url(delete_uri), method="DELETE", body=file_json)
        self.assert_api_response(response)

        # try to delete already deleted file
        response = yield self.http_client.fetch(self.get_url(delete_uri), method="DELETE", body=file_json)
        self.assert_api_response_fail(response)

        # get deleted file
        download_uri = '/files/' + file_upload_id
        response = yield self.http_client.fetch(self.get_url(download_uri), method="GET")
        self.assert_api_response_fail(response)


    @gen_test(timeout=10)
    def test_post_invalid_file(self):

        # filename
        filename = self.generate_filename()

        # get user sample course edition
        response = yield self.fetch_assert(self.get_url('/courseseditions'))
        json_body = escape.json_decode(response.body)
        term_id = json_body['data'][0][fields.TERM_ID]
        course_id = json_body['data'][0][fields.COURSE_ID]

        # invalid json fileds
        file_json = json.dumps({
            fields.COURSE_ID: course_id,
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_based64_encoded,
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response_fail(response)

        # post file without base64 encoding
        file_json = json.dumps({
            fields.TERM_ID: term_id,
            fields.COURSE_ID: course_id,
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_based64_decoded
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response_fail(response)

        # post a file with eicar
        file_json = json.dumps({
            fields.TERM_ID: "term_idXX",
            fields.COURSE_ID: "course_idXXX",
            fields.FILE_NAME: "test1123",
            fields.FILE_CONTENT: self.file_based64_with_eicar_encoded
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response(response)

        # file with wirus shouldn't be able to download
        file_upload_id = response[fields.FILE_UPLOAD_ID]
        download_uri = '/files/' + file_upload_id
        response = yield self.http_client.fetch(self.get_url(download_uri), method="GET")
        self.assert_api_response_fail(response)

    @gen_test(timeout=1)
    def test_upload_file_from_invalid_courseedition(self):
        # filename
        filename = self.generate_filename()

        # get user sample course edition
        response = yield self.fetch_assert(self.get_url('/courseseditions'))
        json_body = escape.json_decode(response.body)
        term_id = json_body['data'][0][fields.TERM_ID]
        course_id = json_body['data'][0][fields.COURSE_ID]

        # check invalid course_id
        file_json = json.dumps({
            fields.TERM_ID: term_id,
            fields.COURSE_ID: "BBBB",
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_based64_encoded,
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response_fail(response)

        # check invalid term_id
        file_json = json.dumps({
            fields.TERM_ID: "AAAAX",
            fields.COURSE_ID: course_id,
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_based64_encoded,
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response_fail(response)

        # check invalid course_id and term_id
        file_json = json.dumps({
            fields.TERM_ID: "ZZ",
            fields.COURSE_ID: "YY",
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_based64_encoded,
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response_fail(response)

    @gen_test(timeout=1)
    def test_get_and_delete_file_from_not_my_courseedition(self):
        # filename
        filename = self.generate_filename()

        # get user sample course edition
        response = yield self.fetch_assert(self.get_url('/courseseditions'))
        json_body = escape.json_decode(response.body)
        term_id = json_body['data'][0][fields.TERM_ID]
        course_id = json_body['data'][0][fields.COURSE_ID]

        # upload a file
        file_json = json.dumps({
            fields.TERM_ID: term_id,
            fields.COURSE_ID: course_id,
            fields.FILE_NAME: filename,
            fields.FILE_CONTENT: self.file_based64_encoded,
        })
        response = yield self.http_client.fetch(self.get_url('/files'), method="POST", body=file_json)
        self.assert_api_response(response)
        file_upload_id = response[fields.FILE_UPLOAD_ID]

        # switch to another user
        # TODO: ???

        # download file that is not in my course_id/term_id
        download_uri = '/files/' + file_upload_id
        response = yield self.http_client.fetch(self.get_url(download_uri), method="GET")
        self.assert_api_response_fail(response)

        # try to delete not my file
        download_uri = '/files/' + file_upload_id
        response = yield self.http_client.fetch(self.get_url(download_uri), method="DELETE")
        self.assert_api_response_fail(response)


    @gen_test(timeout=1)
    def test_get_list_of_files(self):
        pass
