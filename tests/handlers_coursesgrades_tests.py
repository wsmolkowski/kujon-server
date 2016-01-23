from tornado.testing import AsyncHTTPTestCase
import server

TEST_PORT = 9999

class ApiCoursesGradesTest(AsyncHTTPTestCase):

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

    # Courses

    def testShouldPresentEmptyPageForGetCoursesForUser(self):
        response = self.fetch("/api/courses")
        self.assertEqual(response.code, 400)

    def testShouldPresentCoursesForUser(self):
        response = self.fetch("/api/courses?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 200)

    # Grades

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




