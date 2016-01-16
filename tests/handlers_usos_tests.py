from tornado.testing import AsyncHTTPTestCase

import server

TEST_PORT = 9999


class ApiUsosTest(AsyncHTTPTestCase):

    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app

    def testShouldGetUsoses(self):
        response = self.fetch('/api/usoses')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith('[{\"name\": \"Uniwersyst Warszawski\"'))

    # TODO:

