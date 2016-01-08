import unittest
from datetime import datetime

from user import UsersForTests
from usos import USOSUpdater
from usosinstance import UsosInstances


class UsosupdaterTest(unittest.TestCase):


    def testShouldGetUserInformation(self):

        usoses = UsosInstances()
        usos = usoses.getbyid("UW")

        testusers=UsersForTests();
        user = testusers.getrandombyusosid("UW")

        updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, user.access_token_key, user.access_token_secret)

        url = "services/users/user?fields=id|first_name|last_name|student_status|sex|email|student_programmes|student_number|has_email|titles"

        data = updater.request(url)
        print url
        print data
        self.assertIsNotNone(data)

    def testShouldGetCourseEditions(self):
        usoses = UsosInstances()
        usos = usoses.getbyid("UW")

        testusers=UsersForTests();
        user = testusers.getrandombyusosid("UW")

        updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, user.access_token_key, user.access_token_secret)

        url = "services/grades/course_edition?course_id=E-2IZ2-1004-s3&term_id=2014/15-1"
        data = updater.request(url)
        print url
        print data
        self.assertIsNotNone(data)


    def testShouldGetPlan(self):

        usoses = UsosInstances()
        usos = usoses.getbyid("UW")

        testusers=UsersForTests();
        user = testusers.getrandombyusosid("UW")

        updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, user.access_token_key, user.access_token_secret)

        url="services/tt/student?start=" + str(datetime.now().date()) + "&days=1"
        data = updater.request(url)
        print url
        print data
        self.assertIsNotNone(data)