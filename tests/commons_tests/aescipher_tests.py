# coding=utf-8
import unittest
from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient

from commons.AESCipher import AESCipher
from commons.config import Config
from commons.constants import fields, collections
from commons.usosinstances import USOSINSTANCES
from scripts.dbutils import DbUtils

USER_DOC = {"access_token_key": "es2m5qG6saezBwzFFWE5", "usos_user_id": "15822", "usos_paired": True,
            "user_created": datetime.now(), "usos_id": "PS", "update_time": datetime.now(),
            "name": "kujon test",
            "user_type": "google", "access_token_secret": "c6EF3tZUaqpCpszVhBNxehwLWbN2ML2jvTfpkpMx",
            "created_time": datetime.now(),
            "email": "kujontest@gmail.com"}


class AESCipherTest(unittest.TestCase):
    def testAESCipher(self):
        # assume
        aes = AESCipher()

        usos = USOSINSTANCES[0]

        # when
        encrypted = aes.encrypt_usos(usos)

        # then
        decrypted = aes.decrypt_usos(encrypted)
        self.assertEquals(usos, decrypted)


class CookieEncrtyptTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Config('tests')
        self.dbu = DbUtils(self.config)
        self.client_db = MongoClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]
        self.aes = AESCipher(self.config.AES_SECRET)

    def setUp(self):
        super(CookieEncrtyptTests, self).setUp()
        self.dbu.drop_collections()

    def tearDown(self):
        super(CookieEncrtyptTests, self).tearDown()

    def testCookieEncrtypt(self):
        # assume
        self.user_id = self.client_db[collections.USERS].insert(USER_DOC)

        # when
        cookie_encrypted = self.aes.encrypt(str(self.user_id))

        cookie_decrypted = self.aes.decrypt(cookie_encrypted)

        user = self.client_db[collections.USERS].find_one(
            {fields.MONGO_ID: ObjectId(cookie_decrypted.decode())})

        # then
        self.assertIsNotNone(user)
        self.assertEqual(USER_DOC[fields.ACCESS_TOKEN_KEY], user[fields.ACCESS_TOKEN_KEY])
        self.assertEqual(USER_DOC[fields.ACCESS_TOKEN_SECRET], user[fields.ACCESS_TOKEN_SECRET])
