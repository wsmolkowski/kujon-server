MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'db-for-tests'

from tornado.testing import AsyncTestCase
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

    @tornado.gen.coroutine
    def recreate_dictionaries(self):
        yield self.crowler.recreate_dictionaries()

    def tearDown(self):
        self.stop()

    def testRecreateDictionaries(self):
        # assume - run crowler
        self.io_loop.run_sync(self.recreate_dictionaries)

        # then - check if tables are filled
        result = self.dao.count(constants.COLLECTION_COURSES_CLASSTYPES)
        self.assertNotEqual(0, result)
