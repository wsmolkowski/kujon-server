from tornado.testing import AsyncHTTPTestCase

import server

TEST_PORT = 9999


class ApiUserTest(AsyncHTTPTestCase):

    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app


    def testPresentErrorPageForGetUser(self):
        response = self.fetch('/api/user')
        self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><head><title>404:'))

    def testShouldNotGetUser(self):
        response = self.fetch('/api/user?a=1&b=1&b=3&d=4')
        # self.assertEqual(response.code, 404)
        self.assertTrue(response.body.startswith('<html><head><title>404:'))

    def testShouldGetUser(self):
        #TODO: change this test to remove user, create user, check for user, and remove user
        response = self.fetch('/api/user?mobile_id=2&usos_id=UW&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith('{\"last_name\": \"'))

    def testShouldFailNonExistingTokenKey(self):
        response = self.fetch('/api/grades?mobile_id=2&usos_id=UW&course_id=xxx&term_id=xxx&access_token_key=FAKE&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 404)

    def testShouldPresentEmptyPageForGetCoursesForUser(self):
        response = self.fetch('/api/courses')
        self.assertEqual(response.code, 404)
        self.assertTrue("Not Found" in response.body)

    def testShouldGetCoursesForUser(self):
        response = self.fetch('/api/grades?mobile_id=1&usos_id=UW&course_id=1000-612ARR&term_id=2004/TZ&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertTrue("course_id" in response.body)

    def testShouldLogoutUserForGivenSessionId(self):
        self.assertFalse("do zaimplementowani")

    def testShouldNotLogoutUserforNotUserSessionId(self):
        self.assertFalse("do zaimplementowani")
