MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'db-for-tests'

from tornado.testing import AsyncTestCase

from usosapi import constants
from usosapi.usoscrowler import UsosCrowler
from usosapi.mongo_dao import Dao


class TestHelper(AsyncTestCase):

    def setUp(self):
        self.dao = Dao(dburi=MONGODB_URI, dbname=MONGODB_NAME)
        self.crowler = UsosCrowler(dao=self.dao)

        self.beforeTest()

    def beforeTest(self):
        self.dao.drop_collections()
        self.crowler.prepare_database()

    def tearDown(self):
        self.stop()


class CrowlerTest(TestHelper):
    def testRecreateDictionaries(self):

        # assume - run clower
        self.crowler.recreate_dictionaries()

        # then - check if tables are filled
        result = self.dao.count(constants.COLLECTION_COURSES_EDITIONS)
        self.assertNotEqual(0, result)

        result = self.dao.count(constants.COLLECTION_COURSES_CLASSTYPES)
        self.assertNotEqual(0, result)
