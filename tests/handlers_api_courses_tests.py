from tornado.testing import AsyncHTTPTestCase
import server

TEST_PORT = 9999

class ApiCoursesTest(AsyncHTTPTestCase):

    #TODO: change this test to remove user, create user, check for user, and remove user
    access_token_key = "3ShYQv8LyvgeXthKJzmJ"
    access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
    mobile_id = "3"
    usos_id = "UW"
    auth_uri = "mobile_id={0}&usos_id={1}&access_token_key={2}&access_token_secret={3}".format(mobile_id,usos_id,access_token_key,access_token_secret)

    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app

    # courseseditions

    def testShouldPresentEmptyPageForGetCoursesForUser(self):
        response = self.fetch("/api/courseseditions")
        self.assertEqual(response.code, 400)

    def testShouldPresentCoursesForUser(self):
        response = self.fetch("/api/courseseditions?{0}".format(self.auth_uri))
        self.assertTrue('"course_id": "1000-612ARR", "term_id": "2004/TZ", "course_name": {"en": "Distributed and Parallel Algorithms", "pl": "Algorytmy rozproszone i r\u00f3wnoleg\u0142e"}}' in response.body)
        self.assertEqual(response.code, 200)

    def testShouldFailForWrongUser(self):
        response = self.fetch("/api/courseseditions?mobile_id=FAKE&usos_id={0}&access_token_key={1}&access_token_secret={2}".format(self.usos_id,self.access_token_key,self.access_token_secret))
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



