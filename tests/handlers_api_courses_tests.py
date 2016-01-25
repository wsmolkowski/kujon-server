from tests_base import TestBaseClassApp

class ApiCoursesTest(TestBaseClassApp):

    # courseseditions

    def testShouldPresentEmptyPageForGetCoursesForUser(self):
        response = self.fetch("/api/courseseditions")
        self.assertEqual(response.code, 400)

    def testShouldPresentCoursesForUser(self):
        response = self.fetch("/api/courseseditions?{0}".format(self.auth_uri))
        self.assertTrue('"course_id": "1000-612ARR", "term_id": "2004/TZ", "course_name": {"en": "Distributed and Parallel Algorithms", "pl": "Algorytmy rozproszone i r\u00f3wnoleg\u0142e"}}' in response.body)
        self.assertEqual(response.code, 200)

    def testShouldFailForWrongUser(self):
        response = self.fetch("/api/courseseditions?mobile_id=FAKE&usos={0}&access_token_key={1}&access_token_secret={2}".format(self.usos,self.access_token_key,self.access_token_secret))
        self.assertEqual(response.code, 400)

    # courses

    def testShouldReturnGivenCourse(self):
        response = self.fetch("/api/courses/1000-612ARR?{0}".format(self.auth_uri))
        self.assertTrue('"id": "1000-612ARR"' in response.body)
        self.assertEqual(response.code, 200)

        response = self.fetch("/api/courses/1000-621MRB?{0}".format(self.auth_uri))
        self.assertTrue('"id": "1000-621MRB"' in response.body)
        self.assertEqual(response.code, 200)

    def testShouldnotReturnForFakeCourse(self):
        response = self.fetch("/api/courses/FAKE?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)



