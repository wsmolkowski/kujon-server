import unittest

from usosapi.usosutils.usosclient import UsosClient


class ClientTest(unittest.TestCase):
    def setUp(self):
        base_url = "https://usosapps.uw.edu.pl/"
        access_token_key = "3ShYQv8LyvgeXthKJzmJ"
        access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
        consumer_key = "KBt6uWPWUekUzFtNTyY9"
        consumer_secret = "Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG"

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

        # when
        response = self.client.course_info(course_id)

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
