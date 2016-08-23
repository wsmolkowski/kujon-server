# coding=utf-8

import logging

from pymongo import MongoClient
from tornado.testing import AsyncTestCase, gen_test

from commons import constants
from commons.config import Config
from crawler.UsosCrawler import UsosCrawler
from scripts.dbutils import DbUtils
from tests.base import USER_DOC


class CrawlerTest(AsyncTestCase):
    @classmethod
    def setUpClass(self):
        self.config = Config('tests')
        self.dbu = DbUtils(self.config)
        self.client_db = MongoClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]

    def setUp(self):
        super(CrawlerTest, self).setUp()
        self.dbu.drop_collections()
        self.dbu.recreate_database(self.config.AES_SECRET)

        self.assertNotEqual(0, self.client_db[constants.COLLECTION_USOSINSTANCES].count())

        self.user_id = self.client_db[constants.COLLECTION_USERS].insert(USER_DOC)
        logging.info(self.user_id)

    def tearDown(self):
        super(CrawlerTest, self).tearDown()
        self.stop()

    @gen_test(timeout=300)
    def testInitialUserCrawl(self):
        # assume - run crawler
        yield UsosCrawler(self.config).initial_user_crawl(self.user_id)

        # then - check if tables are filled
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_USERS_INFO].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_COURSES_EDITIONS].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_THESES].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_TERMS].count())
        # self.assertNotEqual(0, self.client_db[constants.COLLECTION_COURSES_CLASSTYPES].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_FACULTIES].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_PROGRAMMES].count())

    @gen_test(timeout=300)
    def testInitialUserCrawlRefresh(self):
        # assume - run crawler
        yield UsosCrawler(self.config).initial_user_crawl(self.user_id, refresh=True)

        # then - check if tables are filled
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_USERS_INFO].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_COURSES_EDITIONS].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_THESES].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_TERMS].count())
        # self.assertNotEqual(0, self.client_db[constants.COLLECTION_COURSES_CLASSTYPES].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_FACULTIES].count())
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_PROGRAMMES].count())

    @gen_test(timeout=30)
    def testArchiveUser(self):
        # assume - run crawler
        yield UsosCrawler(self.config).archive_user(self.user_id)

        # then - check if tables are filled
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_USERS_ARCHIVE].count())

    @gen_test(timeout=30)
    def testSubscribe(self):
        # assume - run crawler
        yield UsosCrawler(self.config).subscribe(self.user_id)

        # then - check if tables are filled
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_SUBSCRIPTIONS].count())

    @gen_test(timeout=30)
    def testProcessEvent(self):
        event = {u'entry': [
            # {u'operation': u'update', u'node_id': 62109, u'related_user_ids': [u'1279833'], u'time': 1467979077},
            # {u'operation': u'update', u'node_id': 58746, u'related_user_ids': [u'1279833'], u'time': 1467979077},
            # {u'operation': u'update', u'node_id': 55001, u'related_user_ids': [u'1279833'], u'time': 1467979077},
            {u'operation': u'update', u'node_id': 62109, u'related_user_ids': [u'1167405'], u'time': 1467979077},
            {u'operation': u'update', u'node_id': 58746, u'related_user_ids': [u'1167405'], u'time': 1467979077},
            {u'operation': u'update', u'node_id': 55001, u'related_user_ids': [u'1167405'], u'time': 1467979077}
        ],
            u'event_type': u'crstests/user_point', u'usos_id': u'DEMO'}
        # await crawler.process_event(event)

        # assume - run crawler
        yield UsosCrawler(self.config).process_event(event)

        # then - check if tables are filled
        self.assertNotEqual(0, self.client_db[constants.COLLECTION_MESSAGES].count())
