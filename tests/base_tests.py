from tornado.testing import AsyncHTTPTestCase

import server

class TestHelloApp(AsyncHTTPTestCase):
    def get_app(self):
        return server.Application

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Hello, world')
