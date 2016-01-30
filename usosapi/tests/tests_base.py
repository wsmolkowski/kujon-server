from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from usosapi import server
from datetime import datetime
import constants

class TestBaseClassApp(AsyncHTTPTestCase):
    #TODO: change this test to remove user, create user, check for user, and remove user
    access_token_key = "3ShYQv8LyvgeXthKJzmJ"
    access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
    mobile_id = "w1"
    usos = "UW"
    user_id = None
    auth_uri = None

    @classmethod
    def setUpClass(self):
        print "Preparing tests for class: {0}".format(self.__name__)
        # TODO: przeniesc to aby wykonalo sie raz na samym poczatku
        self.app = server.Application()
        self.app.dao.drop_collections()
        self.app.dao.prepare()

        print "Creating user {0} for tests for Usos: {1}.".format(self.mobile_id,self.usos)
        user_id = {constants.USOS_ID: self.usos, constants.MOBILE_ID: self.mobile_id,
                  constants.ACCESS_TOKEN_SECRET: self.access_token_secret,
                  constants.ACCESS_TOKEN_KEY: self.access_token_key, constants.CREATED_TIME: datetime.now()}
        # TODO: change users to constants.COLLECTION_USERS
        userdocid = self.app.dao.insert('users', user_id)
        self.user_id = userdocid
        self.auth_uri = "mobile_id={0}&user_id={1}&usos={2}&access_token_key={3}&access_token_secret={4}".format(self.mobile_id,self.user_id,self.usos,self.access_token_key,self.access_token_secret)


    @classmethod
    def tearDownClass(self):
        print "Finishing tests for class: {0}".format(self.__name__)

    def get_app(self):
        return self.app

    def get_new_ioloop(self):
        return IOLoop.instance()






