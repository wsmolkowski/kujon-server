from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from usosapi import server
from datetime import datetime
import motor
import constants

class TestBaseClassApp(AsyncHTTPTestCase):
    #TODO: change this test to remove user, create user, check for user, and remove user
    access_token_key = "3ShYQv8LyvgeXthKJzmJ"
    access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
    mobile_id = "w1"
    usos = "UW"
    auth_uri = "mobile_id={0}&usos={1}&access_token_key={2}&access_token_secret={3}".format(mobile_id,usos,access_token_key,access_token_secret)

    @classmethod
    def setUpClass(self):
        print "Preparing tests for class: {0}".format(self.__name__)
        # TODO: przeniesc to aby wykonalo sie raz na samym poczatku
        self.app = server.Application()
        self.app.dao.drop_collections()
        self.app.dao.prepare()
        print "Creating user {0} for tests for Usos: {1}.".format(self.mobile_id,self.usos)
        userDoc = {constants.USOS_ID: self.usos, constants.MOBILE_ID: self.mobile_id,
                  constants.ACCESS_TOKEN_SECRET: self.access_token_secret,
                  constants.ACCESS_TOKEN_KEY: self.access_token_key, constants.CREATED_TIME: datetime.now()}
        userDocId = motor.Op(self.app.db.users.insert, userDoc)

    @classmethod
    def tearDownClass(self):
        print "Finishing tests for class: {0}".format(self.__name__)

    def get_app(self):
        return self.app

    def get_new_ioloop(self):
        return IOLoop.instance()






