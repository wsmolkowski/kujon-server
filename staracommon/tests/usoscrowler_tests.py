import logging

from bson.objectid import ObjectId
from tornado.testing import AsyncTestCase, gen_test

from staracommon import constants
from staracommon.mongo_dao import Dao
from staracommon.usosutils.usosclient import UsosClient
from staracommon.usosutils.usoscrowler import UsosCrowler

MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'db-for-tests'

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
    def testInitCrowlerDEMO(self):
        # when
        self.user = {"mobile_id": "demo1",
                "access_token_key": "ktNYxsVzmcy5wWFE69PW", "usos_id": "DEMO",
                "access_token_secret": "F7qe9U6Ks7KuLPcJRJRj8XE9uYPSrYz2nV3hQscR"}

        user = self.dao.insert(constants.COLLECTION_USERS, self.user)
        yield self.crowler.initial_user_crowl(ObjectId(str(user)))

        # then
        self.assertTrue((self.dao.count(constants.COLLECTION_USERS)) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USOSINSTANCES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USERS_INFO) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_EDITIONS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_TERMS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_CROWLLOG) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_FACULTIES) > 0)


    @gen_test(timeout=1000)
    def testInitCrowlerUW(self):
        # when
        self.user = {"mobile_id": "uw1",
                "access_token_key": "3ShYQv8LyvgeXthKJzmJ", "usos_id": "UW",
                "access_token_secret": "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"}

        user = self.dao.insert(constants.COLLECTION_USERS, self.user)

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
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_UNITS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_FACULTIES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_GROUPS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_PROGRAMMES) > 0)

    @gen_test(timeout=1000)
    def testInitCrowlerPS(self):
        # assume
        user = {"mobile_id": "ps1",
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
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_UNITS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_FACULTIES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_GROUPS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_PROGRAMMES) > 0)
