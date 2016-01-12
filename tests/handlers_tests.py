from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop

import server
import settings

TEST_PORT = 9999


class ApiUserTest(AsyncHTTPTestCase):
    #def get_new_ioloop(self):
    #    return IOLoop.instance()

    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app


    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Hello, world from database ' + settings.MONGODB_NAME)


    def testPresentErrorPageForGetUser(self):
        response = self.fetch('/api/user')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404:'))


    def testShouldNotGetUser(self):
        response = self.fetch('/api/user?a=1&b=1&b=3&d=4')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404:'))

    def testShouldGetUser(self):
        #TODO: change this test to remove user, create user, check for user, and remove user
        # get data for existing user
        response = self.fetch('/api/user?mobile_id=2&usos_id=UW&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith('{\"last_name\": \"'))

    def testShouldGetErrorPageForCourseAndTermUser(self):
        response = self.fetch('/api/grades')
        self.assertEqual(response.code, 404)

    def testShouldGetErrorWrongParametersCourseAndTermUser(self):
        # check for good support of passed 4 usuported args
        response = self.fetch('/api/grades?a=1&b=1&b=3&d=4')
        self.assertEqual(response.code, 404)

    def testShouldGetGradesForCourseAndTermUser(self):
        response = self.fetch('/api/grades?mobile_id=2&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue("course_name" in response.body)

    def testShouldFailGetGradesForCourseAndTermUser(self):
        # fake course_id
        response = self.fetch('/api/grades?mobile_id=2&usos_id=UW&course_id=FAKE&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 500)

    def testShouldFailNonExistingTokenKey(self):
        response = self.fetch('/api/grades?mobile_id=2&usos_id=UW&course_id=xxx&term_id=xxx&access_token_key=FAKE&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 404)

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


