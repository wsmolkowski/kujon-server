# coding=utf-8

import logging
from datetime import datetime

import motor.motor_tornado
from motor import MotorGridFSBucket
from pymongo import MongoClient
from tornado import escape, gen
from tornado.log import enable_pretty_logging
from tornado.testing import AsyncHTTPTestCase

from commons import utils
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.constants import collections, config
from commons.enumerators import Environment
from scripts.dbutils import DbUtils

USOS_DEMO = {"_id": {"$oid": "585e3c6d11b85839d440669c"}, "validate_ssl_certificate": True,
             "consumer_key": "u9xbMGsj9rfER3QBPCBR", "comment": "OK",
             "consumer_secret": "f6TDvucnwDUJ8ZX7HCFa4kvNEFnE7MzByezgBy5v", "usos_id": "DEMO",
             "name": "Uniwersytet DEMO w Nibylandi", "contact": "dsksysadm@adm.uw.edu.pl",
             "created_time": {"$date": 1482574461247}, "logo": "/static/img/logo/logo-demo-64x64.jpg",
             "url": "https://usosapps.demo.usos.edu.pl/", "enabled": True}

USER_DOC = {"access_token_secret": "RbqLudKTUV3SddKbZ2qqvhGEYTrwBpUUKGcjr39W",
            "name": "kujontest@gmail.com",
            "created_time": datetime.now(),
            "email": "kujontest@gmail.com",
            "email_confirmed": "True",
            "usos_id": "DEMO",
            "usos_paired": "True",
            "user_created": datetime.now(), "device_id": "WWW",
            "password": "xxx",
            "user_type": "EMAIL",
            "update_time": datetime.now(),
            "device_type": "WWW",
            "access_token_key": "zGzZaWNj32HnsYMP69rb",
            "usos_user_id": "1015146"}

TOKEN_DOC = {"user_type": "EMAIL",
             "token": "gAAAAABYZj1qBvTzYre_J1XtkqTAzg0OB7Kn4UB0CGRYqjHLflT4w1Jhzuz7lAqGF2uIrCaV3kkE5FEF54qyHMQbDs13aN6lu7mnAvh1v1a6Z-hNijUle14=",
             "update_time": datetime.now(),
             "user_id": "xxx",
             "email": "kujontest@gmail.com",
             "created_time": datetime.now()}

enable_pretty_logging()
logging.getLogger().setLevel(logging.DEBUG)


class BaseTestClass(AsyncHTTPTestCase):
    @staticmethod
    def insert_user(config, user_doc=None, token_doc=None):

        if not user_doc:
            user_doc = USER_DOC

        client_db = MongoClient(config.MONGODB_URI)[config.MONGODB_NAME]

        user_id = client_db[collections.USERS].insert(user_doc)

        if not token_doc:
            aes = AESCipher(config.AES_SECRET)
            TOKEN_DOC['token'] = aes.encrypt(str(user_id)).decode()
            token_doc = TOKEN_DOC

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

    def setUp(self):
        super(BaseTestClass, self).setUp()

        self.client = utils.http_client(proxy_host=self.config.PROXY_HOST,
                                        proxy_port=self.config.PROXY_PORT,
                                        io_loop=self.io_loop)

        client = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)
        self.db = client[self.config.MONGODB_NAME]
        logging.info(self.db)
        self.aes = AESCipher(self.config.AES_SECRET)
        self.fs = MotorGridFSBucket(self.db)

        self._app.settings[config.APPLICATION_DB] = self.db
        self._app.settings[config.APPLICATION_CONFIG] = self.config
        self._app.settings[config.APPLICATION_AES] = self.aes
        self._app.settings[config.APPLICATION_FS] = self.fs

    @gen.coroutine
    def _assertFetch(self, url, method, body, contentType, headers, body_producer):

        header = {
            config.MOBILE_X_HEADER_EMAIL: USER_DOC['email'],
            config.MOBILE_X_HEADER_TOKEN: TOKEN_DOC['token'],
            config.MOBILE_X_HEADER_REFRESH: 'True',
        }
        # if additional header to add
        if headers:
            for key in headers:
                header[key] = headers[key]

        response = yield self.client.fetch(url, method=method, body=body, headers=header, body_producer=body_producer,
                                           allow_nonstandard_methods=True)

        logging.debug(response.body)

        self.assertEqual(response.code, 200)
        self.assertTrue(contentType in response.headers['Content-Type'])
        return response

    @gen.coroutine
    def assertOK(self, url, method='GET', body=None, contentType='application/json', headers=None, body_producer=None):

        response = yield self._assertFetch(url, method, body, contentType, headers, body_producer)

        if contentType == 'application/json':
            json_body = escape.json_decode(response.body)
            self.assertIsNotNone(json_body)
            self.assertEqual('success', json_body['status'])
            return json_body
        else:
            # not json, e.g. image nothing to test
            pass

    @gen.coroutine
    def assertFail(self, url, method='GET', body=None, contentType='application/json', headers=None, body_producer=None):

        response = yield self._assertFetch(url, method, body, contentType, headers, body_producer)

        if contentType == 'application/json':
            json_body = escape.json_decode(response.body)
            self.assertIsNotNone(json_body)
            self.assertTrue(json_body['status'] in ('usos', 'error',))
            self.assertNotEqual(200, json_body['code'])
            return json_body
        else:
            # not json, e.g. image notihing to test
            pass
