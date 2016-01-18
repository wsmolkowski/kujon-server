import urlparse
from datetime import datetime

import motor
import tornado.web

import constants
import oauth2 as oauth
import settings
import usosmixin
from handlers_api import BaseHandler


class MainHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.render("base.html", title=settings.PROJECT_TITLE)
        else:
            self.redirect("/authentication/login")


class LoginHandler(BaseHandler):
    def get(self):
        data = {constants.NEXT_PAGE: self.get_argument('next', '/')}
        self.render("login.html", title=settings.PROJECT_TITLE, **data)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        access_token_key = self.get_argument("inputAccessTokenKey")
        access_token_secret = self.get_argument("inputAccessTokenSecret")
        next_page = self.get_argument(constants.NEXT_PAGE, "/")

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: access_token_key},
                                                constants.USER_PRESENT_KEYS)
        if user_doc:
            self.set_secure_cookie(constants.USER_SECURE_COOKIE, str(user_doc))
            self.redirect(next_page)
        else:
            data = {
                'alert_message': "login authentication failed for {0} and {1}".format(access_token_key,
                                                                                      access_token_secret),
                constants.NEXT_PAGE: next_page
            }

            self.render("login.html", title=settings.PROJECT_TITLE, **data)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(constants.USER_SECURE_COOKIE)
        self.redirect("/")


class CreateUserHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def render_create2(self, data=dict()):

        usoses = yield self.db.usosinstances.find().to_list(length=100)
        update = dict({"usoses" : usoses})
        update.update(data)
        self.render("create.html", title=settings.PROJECT_TITLE, **update)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        usoses = yield self.db.usosinstances.find().to_list(length=100)
        data = {
            'usoses': usoses
        }
        self.render("create.html", title=settings.PROJECT_TITLE, **data)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        mobile_id = self.get_argument("mobile_id").strip()
        usos_url = self.get_argument("usos").strip()

        usos_doc = yield self.db.usosinstances.find_one({constants.URL: usos_url})

        # try to find user in db
        user = yield self.db.users.find_one({constants.MOBILE_ID: mobile_id, constants.USOS_ID: usos_doc[constants.USOS_ID]})
        if user:
            usoses = yield self.db.usosinstances.find().to_list(length=100)
            data = {
                "alert_message": "mobile_id / username: {0} already exists".format(mobile_id),
                "usoses": usoses
            }
            self.render("create.html", title=settings.PROJECT_TITLE, **data)
        else:
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])
            request_token_url = usos_doc[constants.URL] + 'services/oauth/request_token?scopes=studies|offline_access'
            client = oauth.Client(consumer)
            resp, content = client.request(request_token_url, "GET", callback_url=settings.CALLBACK_URL)
            if resp['status'] != '200':
                raise Exception("Invalid response %s:\n%s" % (resp['status'], content))

            request_token = self.get_token(content)

            # updating to db user access_token_key & access_token_secret
            access_token_key = request_token.key
            access_token_secret = request_token.secret

            result = dict()
            result[constants.USOS_ID] = usos_doc['usos_id']
            result[constants.MOBILE_ID] = mobile_id
            result[constants.ACCESS_TOKEN_SECRET] = access_token_secret
            result[constants.ACCESS_TOKEN_KEY] = access_token_key
            result[constants.CREATED_TIME] = datetime.now()

            user_doc = yield motor.Op(self.db.users.insert, result)
            print "saved new user in database: {0}".format(user_doc)

            authorize_url = usos_url + 'services/oauth/authorize'
            url_redirect = "%s?oauth_token=%s" % (authorize_url, request_token.key)
            self.redirect(url_redirect)


class VerifyHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        oauth_token_key = self.get_argument("oauth_token")
        oauth_verifier = self.get_argument("oauth_verifier")

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_KEY: oauth_token_key})

        if user_doc:
            usos_doc = yield self.db.usosinstances.find_one({constants.USOS_ID: user_doc[constants.USOS_ID]})

            request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[constants.ACCESS_TOKEN_SECRET])
            request_token.set_verifier(oauth_verifier)
            consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])
            client = oauth.Client(consumer, request_token)
            access_token_url = usos_doc[constants.URL] + 'services/oauth/access_token'
            esp, content = client.request(access_token_url, "GET")

            try:
                access_token = self.get_token(content)
                data = {
                    'alert_message': "user_doc authenticated with mobile_id / username: {0}".format(user_doc[constants.USOS_ID]),
                    constants.NEXT_PAGE: "/"
                }
            except KeyError:
                data = {
                    'alert_message': "failed user_doc authenticate with mobile_id / username: {0}".format(user_doc[constants.USOS_ID]),
                    constants.NEXT_PAGE: "/"
                }
            self.render("login.html", title=settings.PROJECT_TITLE, **data)
        else:
            data = {
                    'alert_message': "user_doc not found for given oauth_token_key:{0}, oauth_verifier: {1}"
                        .format(oauth_token_key, oauth_verifier),
                    constants.NEXT_PAGE: "/"
            }
            self.render("/authorization/create", title=settings.PROJECT_TITLE, **data)


class TestHandler(BaseHandler, usosmixin.UsosMixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("oauth_token", None):
            user = yield self.get_authenticated_user()
            # Save the user using e.g. set_secure_cookie()
            print "usos user authenticated", user
        else:
            yield self.authorize_redirect("/authentication/login")
