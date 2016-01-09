import unittest
from datetime import datetime

from model_tests import UsersForTests
from usosinstance import UsosInstances
from usosupdater import USOSUpdater


class UsosupdaterTest(unittest.TestCase):


    def testShouldGetUserInformation(self):

        usoses = UsosInstances()
        usos = usoses.getbyid("UW")

        testusers=UsersForTests()
        user = testusers.getrandombyusosid("UW")

        updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, user.access_token_key, user.access_token_secret)
        result = updater.request_user_info()
        expected = [u'first_name', u'last_name', u'student_status', u'sex', u'titles', u'has_email', u'student_programmes', u'id', u'student_number', u'email']
        self.assertListEqual(expected, result.keys())


    def testShouldGetCourseEditions(self):
        usoses = UsosInstances()
        usos = usoses.getbyid("UW")

        testusers = UsersForTests()
        user = testusers.getrandombyusosid("UW")

        updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, user.access_token_key, user.access_token_secret)

        result = updater.request_curse_info()

        self.assertListEqual([u'course_editions'], result.keys())


    def testShouldGetPlan(self):

        usoses = UsosInstances()
        usos = usoses.getbyid("UW")

        testusers = UsersForTests()
        user = testusers.getrandombyusosid("UW")

        updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, user.access_token_key, user.access_token_secret)

        url = "services/tt/student?start=" + str(datetime.now().date()) + "&days=1"
        result = updater.request(url)

        self.assertListEqual([123444, ], result)