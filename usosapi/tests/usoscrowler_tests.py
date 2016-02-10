MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'db-for-tests'

import logging

from bson.objectid import ObjectId
from tornado.testing import AsyncTestCase, gen_test

from usosapi import constants
from usosapi.mongo_dao import Dao
from usosapi.usosutils.usosclient import UsosClient
from usosapi.usosutils.usoscrowler import UsosCrowler

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

        self.user = {"mobile_id": "123",
                "access_token_key": "3ShYQv8LyvgeXthKJzmJ", "usos_id": "UW",
                "access_token_secret": "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"}
        user = self.dao.insert(constants.COLLECTION_USERS, self.user)

        self.user_id = str(user)

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
    def testInitialUserCrowlerUW(self):
        # when
        yield self.crowler.initial_user_crowl(ObjectId(self.user_id))

        # then

        self.assertTrue((self.dao.count(constants.COLLECTION_USERS)) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USOSINSTANCES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USERS_INFO) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_EDITIONS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_TERMS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSE_EDITION) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_GRADES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_CROWLLOG) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_PARTICIPANTS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_UNITS) > 0)

    @gen_test(timeout=1000)
    def testInitialUserCrowlerPS(self):
        # assume
        user = {"mobile_id": "l1",
                "access_token_key": "uXLyCGpp5zfHPH4z4brg", "usos_id": "PS",
                "access_token_secret": "VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy"}
        user = self.dao.insert(constants.COLLECTION_USERS, user)

        # when
        yield self.crowler.initial_user_crowl(ObjectId(str(user)))

        # then

        self.assertTrue((self.dao.count(constants.COLLECTION_USERS)) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USOSINSTANCES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USERS_INFO) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_EDITIONS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_TERMS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSE_EDITION) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_GRADES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_CROWLLOG) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_PARTICIPANTS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_UNITS) > 0)
