from datetime import datetime

import motor
import tornado.web

import settings
import constants
from handlers import BaseHandler
import usosupdater
import usosmixin

class MainHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.render("base.html", title=settings.PROJECT_TITLE)
        else:
            self.redirect("/authentication/login")


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
            data = {
                    'alert_message': "login authentication failed for {0} and {1}".format(access_token_key, access_token_secret),
            }

        self.render("login.html", title=settings.PROJECT_TITLE, **data)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(constants.USER_SECURE_COOKIE)
        self.redirect("/")


class CreateUserHandler(BaseHandler):
    def get(self):
        self.render("create.html", title=settings.PROJECT_TITLE)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
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
            print "login authentication failed for {0} and {1}".format(access_token_key, access_token_secret)
            print "creating user url: {0} consumer_key: {1} consumer_secret: {2} access_token_key: {3} access_token_secret: {4}  ".format(
                url, consumer_key, consumer_secret, access_token_key, access_token_secret
            )
            try:
                print url, consumer_key, consumer_secret, access_token_key, access_token_secret
                result = yield usosupdater.request_user_info(url, consumer_key, consumer_secret, access_token_key, access_token_secret)

                result[constants.USOS_ID] = result.pop('id')
                #result[constants.MOBILE_ID] = parameters.mobile_id
                result[constants.ACCESS_TOKEN_SECRET] = access_token_secret
                result[constants.ACCESS_TOKEN_KEY] = access_token_key
                result[constants.CREATED_TIME] = datetime.now()

                user_doc = yield motor.Op(self.db.users.insert, result)

                print "saved new user in database: {0}".format(user_doc)
                self.redirect("/")
            except Exception, ex:
                data = {
                        'alert_message': "User creation fail failed for {0} and {1}".format(access_token_key, access_token_key),
                        'alert_exception': ex,
                }
                print ex
                self.render("create.html", title=settings.PROJECT_TITLE, **data)


class TestHandler(BaseHandler, usosmixin.UsosMixin):

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("oauth_token", None):
            user = yield self.get_authenticated_user()
            # Save the user using e.g. set_secure_cookie()
            print "usos user authenticated", user
        else:
            yield self.authorize_redirect("/authentication/login")
