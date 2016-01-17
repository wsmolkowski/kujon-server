from datetime import datetime

import motor
import tornado.web

import constants
import settings
import usosupdater
from handlers_api import BaseHandler


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
        data = None
        access_token_key = self.get_argument("inputAccessTokenKey")
        access_token_secret = self.get_argument("inputAccessTokenSecret")

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: access_token_key},
                                                 constants.USER_PRESENT_KEYS)
        if user_doc:
            # TODO: zimienic wartosc cookie na cos lepszego
            self.set_secure_cookie(constants.USER_SECURE_COOKIE, "wartosc")
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

        mobile_id = str(self.get_argument("mobileId"))
        access_token_key = str(self.get_argument("inputAccessTokenKey"))
        access_token_secret = str(self.get_argument("inputAccessTokenSecret"))
        url = str(self.get_argument("inputUrl"))
        consumer_key = str(self.get_argument("inputConsumerKey"))
        consumer_secret = str(self.get_argument("inputConsumerSecret"))

        # algorithm for autorization from mobile:
        # mobile asks backend if user exist:
        # sends to /api/user: mobile_id, usos_id, access_token_key and access_token_secret
        # if user exists in backend for given usos_id, access_token_key and access_token_secret
        #   API returns user_id and user data
        # else
        #   backend try to log to USOS with given access_token_key and access_token_secret
        #   if login in USOS OK
        #       update access_token_key and access_token_secret in backend for given usos_id
        #       returns user_id and user data
        #   else
        #       return usos_url, consumer_key, consumer_secret, auth_needed=1 flag for auth in USOS
        #       mobile redirect to given usos url for authorization with consumer_key, consumer_secret
        #       after auth is USOS mobile gets from USOS access_token_key, access_token_secret
        #       mobile sends to /api/user: mobile_id, usos_id, access_token_key and access_token_secret
        #       should get user data
        #

        # response = self.fetch('/api/user?mobile_id={0}&usos_id={1}&access_token_key={&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: access_token_key},
                                                 constants.USER_PRESENT_KEYS)
        if user_doc:
            print "user already exists {0}".format(user_doc)
            # TODO: ustawic wartosc cookie
            self.set_secure_cookie(constants.USER_SECURE_COOKIE, "wartosc coookie")
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

