MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'db-for-tests'

from tornado.testing import AsyncTestCase, gen_test
import tornado.gen
from usosapi import constants
from usosapi.usoscrowler import UsosCrowler
from usosapi.mongo_dao import Dao


class CrowlerTest(AsyncTestCase):

    def setUp(self):
        super(CrowlerTest, self).setUp()

        self.dao = Dao(dburi=MONGODB_URI, dbname=MONGODB_NAME)
        self.crowler = UsosCrowler(dao=self.dao)

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
