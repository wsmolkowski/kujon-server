import logging
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from staraapi import server, constants, settings
from datetime import datetime


TEST_MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
TEST_MONGODB_NAME = 'usos-test2'
TEST_PORT = 7777

class TestBaseClassApp(AsyncHTTPTestCase):

    access_token_key = "3ShYQv8LyvgeXthKJzmJ"
    access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
    mobile_id = "w1"
    usos = "UW"
    user_id = None
    auth_uri = None

    @classmethod
    def setUpClass(self):
        logging.info("Preparing tests for class: {0}".format(self.__name__))

        self.app = server.Application()
        self.app.dao.drop_collections()
        self.app.dao.prepare()

        logging.info("Creating user {0} for tests for Usos: {1}.".format(self.mobile_id,self.usos))
        user_id = {constants.USOS_ID: self.usos, constants.MOBILE_ID: self.mobile_id,
                  constants.ACCESS_TOKEN_SECRET: self.access_token_secret,
                  constants.ACCESS_TOKEN_KEY: self.access_token_key, constants.CREATED_TIME: datetime.now()}

        userdocid = self.app.dao.insert('users', user_id)
        self.user_id = userdocid
        self.auth_uri = "mobile_id={0}&user_id={1}&usos={2}&access_token_key={3}&access_token_secret={4}".format(self.mobile_id,self.user_id,self.usos,self.access_token_key,self.access_token_secret)


    @classmethod
    def tearDownClass(self):
        logging.info("Finishing tests for class: {0}".format(self.__name__))

    def get_app(self):
        return self.app

    def get_new_ioloop(self):
        return IOLoop.instance()

