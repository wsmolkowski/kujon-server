from tornado.testing import AsyncHTTPTestCase

import server
import settings

TEST_PORT = 9999


class ApiUserTest(AsyncHTTPTestCase):
    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app


    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Hello, world from database ' + settings.MONGODB_NAME)


    def testShouldGetUser(self):

        # check call without arguments
        response = self.fetch('/api/user')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404:'))

        # check for good support of passed 4 usuported args
        response = self.fetch('/api/user?a=1&b=1&b=3&d=4')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404:'))

        #TODO: change this test to remove user, create user, check for user, and remove user
        # get data for existing user
        response = self.fetch('/api/user?user_id=2&usos_id=UW&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith('{\"usos_data\": {\"'))

    def testShouldGetGradesForCourseAndTermUser(self):

        # check call without arguments
        response = self.fetch('/api/grades')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404: Not Found'))

        # check for good support of passed 4 usuported args
        response = self.fetch('/api/grades?a=1&b=1&b=3&d=4')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404: Not Found'))

        # get data for existing user
        response = self.fetch('/api/grades?user_id=2&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith('{\"course_id\": \"'))

        # get for nonexisting course_id & term_id
        response = self.fetch('/api/grades?user_id=2&usos_id=UW&course_id=xxx&term_id=xxx&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 400)

    def testShouldGetCoursesForUser(self):
        # pusta strona
        response = self.fetch('/api/courses')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404: Not Found'))

        #for nonexisting user
        response = self.fetch('/api/grades?user_id=-1&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><title>404: Not Found'))

        #for another user not autenticated

        #get courses
        response = self.fetch('/api/grades?user_id=2&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith('{\"course_id\": \"'))


