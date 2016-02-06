MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'db-for-tests'

from bson.objectid import ObjectId
from tornado.testing import AsyncTestCase, gen_test

from usosapi import constants
from usosapi.mongo_dao import Dao
from usosapi.usosutils.usoscrowler import UsosCrowler
from usosapi.usosutils.usosclient import UsosClient

import logging
logging.getLogger().setLevel(logging.DEBUG)


class CrowlerTest(AsyncTestCase):
    def setUp(self):
        super(CrowlerTest, self).setUp()

        self.dao = Dao(dburi=MONGODB_URI, dbname=MONGODB_NAME)
        self.crowler = UsosCrowler(dao=self.dao)
        self.client = UsosClient("https://usosapps.uw.edu.pl/", "KBt6uWPWUekUzFtNTyY9",
                            "Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG",
                            "3ShYQv8LyvgeXthKJzmJ", "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y")

        self.beforeTest()

    def beforeTest(self):
        self.dao.drop_collections()
        self.crowler.drop_collections()
        self.crowler.recreate_usos()

        self.user = {"oauth_verifier": "16076406", "mobile_id": "123",
                "access_token_key": "3ShYQv8LyvgeXthKJzmJ", "usos": "UW",
                "access_token_secret": "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"}
        user_doc = self.dao.insert(constants.COLLECTION_USERS, self.user)

        self.user_id = str(user_doc)

    def tearDown(self):
        self.stop()

    @gen_test
    def testRecreateDictionaries(self):
        # assume - run crowler
        yield self.crowler.recreate_dictionaries()

        # then - check if tables are filled
        result = self.dao.count(constants.COLLECTION_COURSES_CLASSTYPES)
        self.assertNotEqual(0, result)

    @gen_test(timeout=1000)
    def testInitialUserCrowler(self):
        # when
        yield self.crowler.initial_user_crowl(ObjectId(self.user_id))

        # then
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_USERS))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_USERS))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_USOSINSTANCES))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_COURSES_CLASSTYPES))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_USERS_INFO))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_COURSES_EDITIONS))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_TERMS))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_COURSES))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_GRADES))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_CROWLLOG))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_PARTICIPANTS))
        self.assertIsNotNone(self.dao.count(constants.COLLECTION_COURSES_UNITS))


