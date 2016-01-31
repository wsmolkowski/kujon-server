from tests_base import TestBaseClassApp

class ApiGradesTest(TestBaseClassApp):

    # all grades

    def testGradesShouldFailNonExistingTokenKey(self):
        response = self.fetch("/api/grades/?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)

    def testGradesShouldGetGradesForCourseAndTermUser(self):
        response = self.fetch("/api/grades/?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 200)
        self.assertTrue("course_name" in response.body)

    def testGradesShouldFailGetGradesForCourseAndTermUser(self):
        response = self.fetch("/api/grades/?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)

    def testGradesShouldFailGettingGradesForFakeUser(self):
        response = self.fetch("/api/grades/?mobile_id=-1&user_id=FAKE&usos_id=FAKE&access_token_key=FAKE&access_token_secret=FAKE")
        self.assertEqual(response.code, 400)


    # grades for course and term

    def testShouldFailNonExistingTokenKey(self):
        response = self.fetch("/api/grades/course/xxx/xxx?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)

    def testShouldGetGradesForCourseAndTermUser(self):
        response = self.fetch("/api/grades/course/1000-612ARR/2004%2FTZ?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 200)
        self.assertTrue("course_name" in response.body)

    def testShouldFailGetGradesForCourseAndTermUser(self):
        response = self.fetch("/api/grades/course/FAKE/2004%2FTZ?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)

    def testShouldFailGettingGradesForFakeUser(self):
        response = self.fetch("/api/grades/course/1000-612ARR/2004%2FTZ?mobile_id=-1&user_id=FAKE&usos_id=FAKE&access_token_key=FAKE&access_token_secret=FAKE")
        self.assertEqual(response.code, 400)




