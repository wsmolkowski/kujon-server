# coding=utf-8

import unittest

from pymongo import MongoClient

from commons import constants
from commons.config import Config
from commons.enumerators import Environment
from scripts.dbutils import DbUtils

USER_DOC_1 = {"usos_user_id": "1279833", "access_token_key": "j2m28SYPnNXma8csg25M", "email": "user_1@gmail.com",
              "access_token_secret": "59eYAFujVpvLRN7R6uWrMPeQCdxLVYBANduyGnzL", "usos_paired": True,
              "user_type": "google", "usos_id": "DEMO", "name": "dzizes dzizes"}

USER_DOC_2 = {"name": " asd", "access_token_key": "PL63Tfsg72FGfVKayggk", "email": "user_2@gmail.com",
              "access_token_secret": "HWDJM5AWkH3bmh3aVWJkgTpW23SsY7FmjChTV4JR", "usos_paired": True,
              "user_type": "google", "usos_id": "UW"}


class DbUtilsTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config_from = Config(Environment.TESTS.value)
        self.dbu_from = DbUtils(self.config_from)
        self.client_from = MongoClient(self.config_from.MONGODB_URI)
        self.db_from = self.client_from[self.config_from.MONGODB_NAME]

        self.config_to = Config(Environment.DEVELOPMENT.value)
        self.dbu_to = DbUtils(self.config_to)
        self.client_to = MongoClient(self.config_to.MONGODB_URI)
        self.db_to = self.client_from[self.config_to.MONGODB_NAME]

    def setUp(self):
        pass

    def tearDown(self):
        self.client_from.close()
        self.client_to.close()

    def testCopyUuserCrediteltials(self):
        # assume
        self.db_from[constants.COLLECTION_USERS].insert(USER_DOC_1)
        self.db_to[constants.COLLECTION_USERS].insert(USER_DOC_2)

        # when
        self.dbu_from.copy_user_credentials(USER_DOC_1[constants.USER_EMAIL],
                                            USER_DOC_2[constants.USER_EMAIL],
                                            Environment.TESTS.value,
                                            Environment.DEVELOPMENT.value)
        # then
        updated = self.db_to[constants.COLLECTION_USERS].find_one(
            {constants.USER_EMAIL: USER_DOC_2[constants.USER_EMAIL]})

        self.assertIsNotNone(updated)
        self.assertEqual(updated[constants.ACCESS_TOKEN_KEY], USER_DOC_1[constants.ACCESS_TOKEN_KEY])
        self.assertEqual(updated[constants.ACCESS_TOKEN_SECRET], USER_DOC_1[constants.ACCESS_TOKEN_SECRET])
        self.assertEqual(updated[constants.USOS_ID], USER_DOC_1[constants.USOS_ID])
        self.assertEqual(updated[constants.USOS_USER_ID], USER_DOC_1[constants.USOS_USER_ID])
