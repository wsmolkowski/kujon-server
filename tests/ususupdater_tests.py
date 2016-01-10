import unittest
from datetime import datetime

import constants
from mongo_utils import Dao
from usosupdater import USOSUpdater


class UsosupdaterTest(unittest.TestCase):

    def setUp(self):
        self.dao = Dao()

    def testShouldGetUserInformation(self):
        # assume
        usos = self.dao.get_usos('UW')
        user = self.testusers.getrandombyusosid('UW')

        # when
        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET], user.access_token_key, user.access_token_secret)
        result = updater.request_user_info()
        expected = [u'first_name', u'last_name', u'student_status', u'sex', u'titles', u'has_email', u'student_programmes', u'id', u'student_number', u'email']

        # then
        self.assertListEqual(expected, result.keys())


    def testShouldGetCourseEditions(self):
        # assume
        usos = self.dao.get_usos('UW')
        user = self.testusers.getrandombyusosid('UW')

        # when
        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET], user.access_token_key, user.access_token_secret)
        result = updater.request_curse_info()

        # then
        self.assertListEqual([u'course_editions'], result.keys())


    def testShouldGetPlan(self):
        # assume
        usos = self.dao.get_usos('UW')
        user = self.testusers.getrandombyusosid('UW')

        # when
        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET], user.access_token_key, user.access_token_secret)
        url = 'services/tt/student?start=' + str(datetime.now().date()) + '&days=1'
        result = updater.request(url)

        # then
        self.assertIsNotNone(result)
        #self.assertListEqual([123444, ], result)