# coding=utf-8

import logging
from datetime import datetime

import motor.motor_tornado
from motor import MotorGridFSBucket
from pymongo import MongoClient
from tornado import escape
from tornado import gen
from tornado.testing import AsyncHTTPTestCase

from commons import utils
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.constants import collections, config
from commons.enumerators import Environment
from scripts.dbutils import DbUtils

USER_DOC = {"access_token_secret": "59eYAFujVpvLRN7R6uWrMPeQCdxLVYBANduyGnzL",
            "access_token_key": "j2m28SYPnNXma8csg25M",
            "usos_user_id": "1279833",
            "user_created": datetime.now(),
            "name": "dzizes dzizes",
            "created_time": datetime.now(),
            "update_time": datetime.now(),
            "email": "testowy@gmail.com",
            "usos_id": "DEMO",
            "usos_paired": True,
            "user_type": "google",
            "google": {
                "picture": "https://lh3.googleusercontent.com/-f7w-r4iF8DM/AAAAAAAAAAI/AAAAAAAALGo/GDUJeUaHtUo/photo.jpg",
                "email": "testowy@gmail.com",
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImI5Njk3MmI4NjUwZDFjOGNhMmM1NDA0MzhlNGQ5MzUxNzY5ODk0MzIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6Ik83MkVjcGVrSVVPT2xGMWlIVXAxQUEiLCJhdWQiOiI4OTY3NjU3Njg2MjgtYjF0dXQ1ZzZoamluN2lpbjZobjRxbzhsdDNiNmlobHQuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTI1MjEwOTU0NjU0NTA5OTg1MTciLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXpwIjoiODk2NzY1NzY4NjI4LWIxdHV0NWc2aGppbjdpaW42aG40cW84bHQzYjZpaGx0LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiZW1haWwiOiJkeml6ZXM0NTFAZ21haWwuY29tIiwiaWF0IjoxNDcxODY3ODg3LCJleHAiOjE0NzE4NzE0ODd9.PwLfed8_52aydutvkREXHsBcaYHsF2U4E1UQEo5PdaAOE6aJigWqeh4v8GRtYy3IxDzja9j75rkbFP0Hch0elyIDUxrWS2lnDile5TYqiyoXGEfEw6ADvZVq8dVklbGYqg_H5G32tuLUERyleYBWYrPrjJGIRNlEoD2w-Cou2YeHysQl9GNKZl7vmS62HPClPF0jXDQGag_ziHAKBRxl5d4JwC4h3Sg4XunUdUsoq1Ey5F_rAzo5cggCOsQCpXcuSGGWc7YDCDCGBW5JsJsPv6mAi1jgepP5OETMGHC_yrXmQcjUJyctooKVRLRmaLNujlTe95ne-4v8psKOXH_nZQ",
                "access_token": "ya29.CjBHA89EmKP6zkOMrW0K7a3INpF-oZjtyV02aAtwNhrNwqc0_hJM9XoQbuyTbOyCC3I",
                "token_type": "Bearer",
                "name": "testowy@gmail.com",
                "expires_in": datetime.now()},
            }

TOKEN_DOC = {"locale": "pl",
             "name": "imie nazwisko",
             "iat": "1471441024",
             "picture": "https://lh3.googleusercontent.com/-f7w-r4iF8DM/AAAAAAAAAAI/AAAAAAAALGo/GDUJeUaHtUo/photo.jpg",
             "email": "testowy@gmail.com",
             "sub": "101491399228182082844",
             "created_time": datetime.now(),
             "update_time": datetime.now(),
             "login_type": "GOOGLE",
             "alg": "RS256",
             "usos_id": "UWR",
             "given_name": "dzizes451@gmail.com",
             "iss": "https://accounts.google.com",
             "family_name": "dzizes451",
             "email_verified": "true",
             "kid": "a3c737a7b795026217d05be98f8736bd09a69d0d",
             "aud": "896765768628-4tb5sl5l115mcjbavsvgjiinovtifm6p.apps.googleusercontent.com",
             "exp": "1471444624",
             "azp": "896765768628-e6ja58ug43hacq7usqnmn5uakgvnorvd.apps.googleusercontent.com"}


class BaseTestClass(AsyncHTTPTestCase):
    # def get_new_ioloop(self):
    #     return IOLoop.current()

    @staticmethod
    def insert_user(config, user_doc=None, token_doc=None):

        if not user_doc:
            user_doc = USER_DOC

        if not token_doc:
            token_doc = TOKEN_DOC

        client_db = MongoClient(config.MONGODB_URI)[config.MONGODB_NAME]

        user_id = client_db[collections.USERS].insert(user_doc)
        token_id = client_db[collections.TOKENS].insert(token_doc)

        return user_id, token_id

    @staticmethod
    def prepareDatabase(config):
        dbu = DbUtils(config)
        dbu.drop_collections()
        dbu.recreate_database(config.AES_SECRET)

    @classmethod
    def setUpClass(self):
        super(BaseTestClass, self).setUpClass()

        logging.info("Preparing tests for class: {0}".format(self.__name__))
        self.config = Config(Environment.TESTS.value)
        self.client = utils.http_client(self.config.PROXY_HOST, self.config.PROXY_PORT)

        self.db = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]
        logging.info(self.db)
        self.aes = AESCipher(self.config.AES_SECRET)
        self.fs = MotorGridFSBucket(self.db)

    @gen.coroutine
    def fetch_assert(self, url, assert_response=True):
        # request = HTTPRequest(url=self.get_url('/'))
        # with self.assertRaises(tornado.httpclient.HTTPError) as context:
        #     yield self.http_client.fetch(request)

        response = yield self.client.fetch(url, headers={
            config.MOBILE_X_HEADER_EMAIL: USER_DOC['email'],
            config.MOBILE_X_HEADER_TOKEN: USER_DOC['google']['access_token'],
            config.MOBILE_X_HEADER_REFRESH: 'True',
        })

        if assert_response:
            self.assert_api_response(response)

        return response

    def assert_api_response(self, response):
        logging.info(response.body)
        self.assertEqual(response.code, 200)
        self.assertTrue('application/json' in response.headers['Content-Type'])

        json_body = escape.json_decode(response.body)

        self.assertIsNotNone(json_body)
        self.assertEqual('success', json_body['status'])

    def assert_api_response_fail(self, response):
        logging.debug(response.body)
        self.assertEqual(response.code, 200)
        self.assertTrue('application/json' in response.headers['Content-Type'])

        json_body = escape.json_decode(response.body)

        self.assertIsNotNone(json_body)
        self.assertEqual('fail', json_body['status'])
        self.assertNotEqual(200, json_body['code'])
