import logging

from bson.objectid import ObjectId
from tornado.testing import AsyncTestCase, gen_test

from commons import constants
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin
from commons.usosutils.usoscrawler import UsosCrawler

MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'db-for-tests'

logging.getLogger().setLevel(logging.DEBUG)


class CrawlerTest(AsyncTestCase, UsosMixin, DaoMixin):
    def setUp(self):
        super(CrawlerTest, self).setUp()

        self.crawler = UsosCrawler()
        self.beforeTest()

    def beforeTest(self):
        self.dao.drop_collections()
        self.crawler.drop_collections()
        self.crawler.recreate_usos()

    def tearDown(self):
        self.stop()

    @gen_test
    def testRecreateDictionaries(self):
        # assume - run crawler
        yield self.crawler.recreate_dictionaries()

        # then - check if tables are filled
        result = self.dao.count(constants.COLLECTION_COURSES_CLASSTYPES)
        self.assertNotEqual(0, result)

    @gen_test(timeout=1000)
    def testInitCrawlerDEMO(self):
        # when
        self.user = {"mobile_id": "demo1",
                "access_token_key": "sTHHzeBvwcDn4srZRkRU", "usos_id": "DEMO",
                "access_token_secret": "RPKghB2d8y9qGskq698P45ZYuKa9V2XXR2Gv5NUG"}

        user = self.dao.db_insert(constants.COLLECTION_USERS, self.user)
        yield self.crawler.initial_user_crawl(ObjectId(str(user)))

        # then
        self.assertTrue((self.dao.count(constants.COLLECTION_USERS)) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USOSINSTANCES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USERS_INFO) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_EDITIONS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_TERMS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_FACULTIES) > 0)


    @gen_test(timeout=1000)
    def testInitCrawlerUW(self):
        # when
        self.user = {"mobile_id": "uw1",
                "access_token_key": "sTHHzeBvwcDn4srZRkRU", "usos_id": "UW",
                "access_token_secret": "RPKghB2d8y9qGskq698P45ZYuKa9V2XXR2Gv5NUG"}
        user = self.dao.db_insert(constants.COLLECTION_USERS, self.user)

        yield self.crawler.initial_user_crawl(ObjectId(str(user)))

        # then
        self.assertTrue((self.dao.count(constants.COLLECTION_USERS)) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USOSINSTANCES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USERS_INFO) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_EDITIONS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_TERMS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_UNITS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_FACULTIES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_GROUPS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_PROGRAMMES) > 0)

    @gen_test(timeout=1000)
    def testInitCrawlerPS(self):
        # assume
        user = {"mobile_id": "ps1",
                "access_token_key": "uXLyCGpp5zfHPH4z4brg", "usos_id": "PS",
                "access_token_secret": "VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy"}
        user = self.dao.db_insert(constants.COLLECTION_USERS, user)

        # when
        yield self.crawler.initial_user_crawl(ObjectId(str(user)))

        # then
        self.assertTrue((self.dao.count(constants.COLLECTION_USERS)) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USOSINSTANCES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_USERS_INFO) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_EDITIONS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_TERMS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES_UNITS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_COURSES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_FACULTIES) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_GROUPS) > 0)
        self.assertTrue(self.dao.count(constants.COLLECTION_PROGRAMMES) > 0)
