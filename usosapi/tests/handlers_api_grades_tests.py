from tests_base import TestBaseClassApp


class ApiGradesTest(TestBaseClassApp):

    def testShouldFailNonExistingTokenKey(self):
        response = self.fetch("/api/grades?course_id=xxx&term_id=xxx&{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)

    def testShouldGetGradesForCourseAndTermUser(self):
        response = self.fetch("/api/grades?course_id=1000-612ARR&term_id=2004/TZ&{0}".format(self.auth_uri))
        self.assertEqual(response.code, 200)
        self.assertTrue("course_name" in response.body)

    def testShouldFailGetGradesForCourseAndTermUser(self):
        response = self.fetch("/api/grades?course_id=FAKE&term_id=2004/TZ&{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)

    def testShouldFailGettingGradesForFakeUser(self):
        response = self.fetch("/api/grades?course_id=1000-612ARR&term_id=2004/TZ&mobile_id=-1&usos_id=FAKE&access_token_key=FAKE&access_token_secret=FAKE")
        self.assertEqual(response.code, 400)




