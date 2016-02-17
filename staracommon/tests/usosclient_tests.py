import unittest

from staracommon.usosutils.usosclient import UsosClient


class ClientTest(unittest.TestCase):
    def setUp(self):
        base_url = "https://usosapps.demo.usos.edu.pl/"
        access_token_key = "HJTFn9hebBAhFsAckL6K"
        access_token_secret = "7H8VnPPeKAndMP6nGHqrqA9QUStmeGFVwdAe5jmN"
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
