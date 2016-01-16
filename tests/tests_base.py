from tornado.testing import AsyncHTTPTestCase

import server

TEST_PORT = 9999


class TestHelloApp(AsyncHTTPTestCase):
    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app


    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith("\n<!DOCTYPE html>\n<html la"))





