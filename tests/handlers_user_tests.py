from tornado.testing import AsyncHTTPTestCase

import server

TEST_PORT = 9999


class ApiUserTest(AsyncHTTPTestCase):

    #TODO: change this test to remove user, create user, check for user, and remove user
    access_token_key = "3ShYQv8LyvgeXthKJzmJ"
    access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
    mobile_id = "3"
    usos_id = "UW"
    auth_uri = "mobile_id={0}&usos_id={1}&access_token_key={2}&access_token_secret={3}".format(mobile_id,usos_id,access_token_key,access_token_secret)

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app

    def testEmptyUserShouldReturn404(self):
        response = self.fetch('/api/user')
        self.assertEqual(response.code, 400)

    def testShouldNotGetUser(self):
        response = self.fetch('/api/user?a=1&b=1&b=3&d=4')
        self.assertEqual(response.code, 400)

    def testShouldGetUser(self):
        response = self.fetch("/api/user?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 200)
        self.assertTrue('"mobile_id": "3"' in response.body)



