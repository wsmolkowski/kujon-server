from datetime import datetime

import motor
import tornado.web

import settings
import constants
from handlers import BaseHandler
from usosupdater import USOSUpdater


class MainHandler(BaseHandler):
    def get(self):
        self.render("base.html", title=settings.PROJECT_TITLE)


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", title=settings.PROJECT_TITLE)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        access_token_key = self.get_argument("inputAccessTokenKey")
        access_token_secret = self.get_argument("inputAccessTokenSecret")

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: access_token_key},
                                                 constants.USER_PRESENT_KEYS)
        if user_doc:
            self.set_secure_cookie(constants.USER_SECURE_COOKIE, user_doc)
            self.redirect("/")
        else:
            print "login authentication failed for {0} and {1}".format(access_token_key, access_token_key)
            print "creating user"

            self.redirect("/create")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(constants.USER_SECURE_COOKIE)
        self.redirect("/")


class CreateUserHandler(BaseHandler):
    def get(self):
        self.render("create.html", title=settings.PROJECT_TITLE)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        access_token_key = str(self.get_argument("inputAccessTokenKey"))
        access_token_secret = str(self.get_argument("inputAccessTokenSecret"))
        url = str(self.get_argument("inputUrl"))
        consumer_key = str(self.get_argument("inputConsumerKey"))
        consumer_secret = str(self.get_argument("inputConsumerSecret"))

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: access_token_key},
                                                 constants.USER_PRESENT_KEYS)
        if user_doc:
            print "user already exists %s".format(user_doc)
            self.set_secure_cookie(constants.USER_SECURE_COOKIE, user_doc)
            self.redirect("/")
        else:
            print "login authentication failed for {0} and {1}".format(access_token_key, access_token_key)
            print "creating user access_token_key: {0} access_token_secret: {1} url: {2} consumer_key: {3} consumer_secret: {4}".format(
                access_token_key, access_token_secret, url, consumer_key, consumer_secret
            )

            updater = USOSUpdater(url, consumer_key, consumer_secret,
                                  access_token_key, access_token_secret)

            result = updater.request_user_info()


            result[constants.USOS_ID] = result.pop('id')
            #result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.ACCESS_TOKEN_SECRET] = access_token_secret
            result[constants.ACCESS_TOKEN_KEY] = access_token_key
            result[constants.CREATED_TIME] = datetime.now()

            user_doc = yield motor.Op(self.db.users.insert, result)

            print "saved new user in database: {0}".format(user_doc)
            self.redirect("/")