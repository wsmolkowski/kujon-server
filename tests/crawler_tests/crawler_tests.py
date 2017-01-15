# coding=utf-8

import logging

from pymongo import MongoClient
from tornado.testing import AsyncTestCase, gen_test

from commons.config import Config
from commons.constants import collections
from commons.enumerators import Environment
from crawler.UsosCrawler import UsosCrawler
from scripts.dbutils import DbUtils
from tests.base import USER_DOC


class CrawlerTest(AsyncTestCase):
    @classmethod
    def setUpClass(self):
        self.config = Config(Environment.TESTS.value)
        self.dbu = DbUtils(self.config)
        self.client_db = MongoClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]

    def setUp(self):
        super(CrawlerTest, self).setUp()
        self.dbu.drop_collections()
        self.dbu.recreate_database(self.config.AES_SECRET)

        self.assertNotEqual(0, self.client_db[collections.USOSINSTANCES].count())

        self.user_id = self.client_db[collections.USERS].insert(USER_DOC)
        self.usos_id = USER_DOC['usos_id']
        logging.info(self.user_id)

    def tearDown(self):
        super(CrawlerTest, self).tearDown()
        self.stop()

    # @gen_test(timeout=300)
    # def testInitialUserCrawl(self):
    #     # assume - run crawler
    #     yield UsosCrawler(self.config).initial_user_crawl(self.user_id)
    #
    #     # then - check if tables are filled
    #     self.assertNotEqual(0, self.client_db[collections.USERS_INFO].count())
    #     self.assertNotEqual(0, self.client_db[collections.COURSES_EDITIONS].count())
    #     self.assertNotEqual(0, self.client_db[collections.THESES].count())
    #     self.assertNotEqual(0, self.client_db[collections.TERMS].count())
    #     # self.assertNotEqual(0, self.client_db[collections.COURSES_CLASSTYPES].count())
    #     self.assertNotEqual(0, self.client_db[collections.FACULTIES].count())
    #     self.assertNotEqual(0, self.client_db[collections.PROGRAMMES].count())
    #
    # @gen_test(timeout=300)
    # def testInitialUserCrawlRefresh(self):
    #     # assume - run crawler
    #     yield UsosCrawler(self.config).initial_user_crawl(self.user_id, refresh=True)
    #
    #     # then - check if tables are filled
    #     self.assertNotEqual(0, self.client_db[collections.USERS_INFO].count())
    #     self.assertNotEqual(0, self.client_db[collections.COURSES_EDITIONS].count())
    #     self.assertNotEqual(0, self.client_db[collections.THESES].count())
    #     self.assertNotEqual(0, self.client_db[collections.TERMS].count())
    #     # self.assertNotEqual(0, self.client_db[collections.COURSES_CLASSTYPES].count())
    #     self.assertNotEqual(0, self.client_db[collections.FACULTIES].count())
    #     self.assertNotEqual(0, self.client_db[collections.PROGRAMMES].count())

    # @gen_test(timeout=10)
    # def testArchiveUser(self):
    #     # assume - run crawler
    #     yield UsosCrawler(self.config).archive_user(self.user_id)
    #
    #     # then - check if tables are filled
    #     # this is not the best - better test DaoMixin
    #     self.assertEqual(0, self.client_db[collections.USERS_ARCHIVE].count())

    @gen_test(timeout=10)
    def testSubscribe(self):
        # assume - run crawler
        yield UsosCrawler(self.config).subscribe(self.user_id)

        # when check in mongo for expeption from usos
        result = self.client_db[collections.EXCEPTIONS].find_one({"function_name": "subscribe"})

        # then - check if tables are filled
        self.asserEqual('subscribe', result['function_name'])

    def testCrstestPointsNotification(self):
        pass

    def testCrstestGradesNotification(self):
        pass

