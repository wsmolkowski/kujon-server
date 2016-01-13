from tornado.testing import AsyncHTTPTestCase

import server

TEST_PORT = 9999

class ApiCoursesGradesTest(AsyncHTTPTestCase):


    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app

    def testShouldGetGradesForCourseAndTermUser(self):
        response = self.fetch('/api/grades?mobile_id=2&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue("course_name" in response.body)

    def testShouldFailGetGradesForCourseAndTermUser(self):
        # fake course_id
        response = self.fetch('/api/grades?mobile_id=2&usos_id=UW&course_id=FAKE&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 500)

    def testShouldPresentEmptyPageForGetCoursesForUser(self):
        response = self.fetch('/api/courses')
        self.assertEqual(response.code, 404)
        self.assertTrue("Not Found" in response.body)

    def testShouldFailGettingGradesNoAuthentication(self):
        #for nonexisting user - fake access_token_key
        response = self.fetch('/api/grades?mobile_id=-1&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=FAKE&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 404)

    def testShouldGetCoursesForUser(self):
        #get courses
        response = self.fetch('/api/grades?mobile_id=1&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue("course_id" in response.body)


