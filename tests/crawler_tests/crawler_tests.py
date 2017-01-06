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

    @gen_test(timeout=10)
    def testArchiveUser(self):
        # assume - run crawler
        yield UsosCrawler(self.config).archive_user(self.user_id)

        # then - check if tables are filled
        # this is not the best - better test DaoMixin
        self.assertEqual(0, self.client_db[collections.USERS_ARCHIVE].count())

    @gen_test(timeout=10)
    def testSubscribe(self):
        # assume - run crawler
        yield UsosCrawler(self.config).subscribe(self.user_id)

        # when check in mongo for expeption from usos
        result = self.client_db[collections.EXCEPTIONS].find_one({"function_name": "subscribe"})

        # then - check if tables are filled
        self.asserEqual('subscribe', result['function_name'])

    @gen_test(timeout=10)
    def testProcessEvent(self):

        # assume - not notification to get
        event1 = {'operation': 'update', 'node_id': 62109, 'related_user_ids': '1015146', 'time': 1467979077}

        # when
        result1 = yield UsosCrawler(self.config)._user_event(event1['related_user_ids'], event1['node_id'], self.usos_id,
                                                   'crstests/user_grade', event1['operation'])
        # then
        self.assertEqual(result1, 'No notification for type: crstest/user_grade')

        # assume user not exist
        event2 = {'operation': 'update', 'node_id': 58746, 'related_user_ids': 'XXX', 'time': 1467979077}
        # when
        result2 = yield UsosCrawler(self.config)._user_event(event2['related_user_ids'], event2['node_id'], self.usos_id,
                                                   'crstests/user_point', event2['operation'])
        # then should return False
        self.assertEqual(False, result2)

        # assume - not notification to get
        event2['related_user_ids'] = '1015146'
        # when
        result2 = yield UsosCrawler(self.config)._user_event(event2['related_user_ids'], event2['node_id'], self.usos_id,
                                                   'crstests/user_point', event2['operation'])
        # then should return False
        self.assertEqual(result2, 'No notification for type: crstest/user_point')

    @gen_test(timeout=5)
    def testNotificationMessageFormaterGrades(self):

        # assume -
        user_grade = {'node_id': 23348, 'private_comment': '', 'course_name': 'Hydraulika i hydrologia',
                      'grader': 'Szymon Firląg', 'grader_id': 92803, 'student_id': 1100392, 'public_comment': '',
                      'grade': {'symbol': '4,5', 'order_key': 2,
                                'name': 'cztery i pół', 'passes': True, 'decimal_value': '4.5'},
                      'last_changed': '2017-01-02 13:57:08'}

        empty_user_grade = dict()

        # when try - empty values
        UsosCrawler(self.config)._message_formater_crstests_user_grade(empty_user_grade, 'create')

        # when
        notif, title, mess  = UsosCrawler(self.config)._message_formater_crstests_user_grade(user_grade, 'create')

        # then
        self.assertEquals(notif, "Wpisano ocenę: 4.5 ze sprawdzianu (Hydraulika i hydrologia) - zalicza")
        self.assertEquals(title, "Powiadomienie - Wpisano ocenę: 4.5 ze sprawdzianu (Hydraulika i hydrologia) - zalicza")

    def testNotificationMessageFormaterPoints(self):
        # assume -

        user_points = {'grader': 'Magdalena Skolimowska-Kulig', 'points': 10.0, 'comment': '',
                       'last_changed': '2017-01-03 23:10:35', 'student_id': 191953, 'grader_id': 1437,
                       'node_id': 26160, 'course_name': 'Elementy matematyki w ekonomii'}

        empty_user_points = dict()

        # when try - empty values
        UsosCrawler(self.config)._message_formater_crstests_user_point(empty_user_points, 'create')

        # when
        notif, title, mess = UsosCrawler(self.config)._message_formater_crstests_user_point(user_points, 'create')

        # then
        self.assertEquals(notif, "Wpisano punty: 10.0 ze sprawdzianu (Elementy matematyki w ekonomii)")
        self.assertEquals(title, "Powiadomienie - Wpisano punkty: 10.0 ze sprawdzianu (Elementy matematyki w ekonomii)")

    def testCrstestPointsNotification(self):
        pass

    def testCrstestGradesNotification(self):
        pass

