from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase

from usosapi import server

class TestBaseClassApp(AsyncHTTPTestCase):
    #TODO: change this test to remove user, create user, check for user, and remove user
    access_token_key = "3ShYQv8LyvgeXthKJzmJ"
    access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
    mobile_id = "3"
    usos = "UW"
    auth_uri = "mobile_id={0}&usos={1}&access_token_key={2}&access_token_secret={3}".format(mobile_id,usos,access_token_key,access_token_secret)

    def get_app(self):
        return self.app

    def get_new_ioloop(self):
        return IOLoop.instance()

    @classmethod
    def setUpClass(self):
        print "Preparing tests for class: {0}".format(self.__name__)
        self.app = server.Application()

    @classmethod
    def tearDownClass(self):
        print "Finishing tests for class: {0}".format(self.__name__)

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body.startswith("\n<!DOCTYPE html>\n<html la"))





