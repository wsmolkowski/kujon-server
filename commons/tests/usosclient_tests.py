import unittest

from commons.usosutils.usosclient import UsosClient


class ClientTest(unittest.TestCase):
    def setUp(self):
        base_url = "https://usosapps.demo.usos.edu.pl/"
        access_token_key = "YEvjLEYU5vSgd3R9pvxu"
        access_token_secret = "s9D4Ca2hMfM6b3dwTs5LrMb6AhadejN8Va5vdGrV"
        consumer_key = "b9MHLmXygtGDbcL5BCj3"
        consumer_secret = "4TQESZkkBMFCT2JgtnzAtD5XG6ACZjsEb5vTrDGM"

        self.client = UsosClient(base_url=base_url,
                                 consumer_key=consumer_key,
                                 consumer_secret=consumer_secret,
                                 access_token_key=access_token_key,
                                 access_token_secret=access_token_secret)

    def testUserInfo(self):
        # when
        response = self.client.user_info("UW")

        # then
        self.assertIsNotNone(0, len(response))

    def testCourseEditionsInfo(self):
        # when
        response = self.client.courseeditions_info()

        # then
        self.assertIsNotNone(0, len(response))

    def testCourseInfo(self):
        # assume
        course_id = "1000-612ARR"
        term_id = "2004/TZ"

        # when
        response = self.client.course_edition(course_id, term_id, fetch_participants=True)

        # then
        self.assertIsNotNone(0, len(response))

    def testGradesForTermAndCourse(self):
        # assume
        course_id = "1000-612ARR"
        term_id = "2004/TZ"

        # when
        response = self.client.grades(course_id, term_id)

        # then
        self.assertIsNotNone(0, len(response))

    def testClassTypes(self):
        # when
        response = self.client.class_types()

        # then
        self.assertIsNotNone(0, len(response))

    def testSubscribeUserGrade(self):
        # when
        response = self.client.subscribe('crstests/user_grade', '571d0ec7855ef92a48fa9b02')

        # then
        self.assertIsNotNone(0, len(response))

    def testSubscribeGrade(self):
        # when
        response = self.client.subscribe('grades/grade', '571d0ec7855ef92a48fa9b02')

        # then
        self.assertIsNotNone(0, len(response))

    def testSubscribeUserPoint(self):
        # when
        response = self.client.subscribe('crstests/user_point', '571d0ec7855ef92a48fa9b02')

        # then
        self.assertIsNotNone(0, len(response))

    def testSubscriptions(self):
        # when
        response = self.client.subscriptions()

        # then
        self.assertIsNotNone(0, len(response))

    def testUnsubscribe(self):
        # when
        response = self.client.unsubscribe()

        # then
        self.assertIsNotNone(0, len(response))
