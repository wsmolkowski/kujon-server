import urlparse

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
                    'alert_message': "login authentication failed for {0} and {1}".format(access_token_key, access_token_secret),
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
    def get(self):
        usoses = yield self.db.usosinstances.find().to_list(length=100)
        data = {
            'usoses': usoses
        }
        self.render("create.html", title=settings.PROJECT_TITLE, **data)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        usos_url = self.get_argument("usos").strip()

        usos_doc = yield self.db.usosinstances.find_one({constants.URL: usos_url})

        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        request_token_url = usos_url + 'services/oauth/request_token?scopes=studies|offline_access'

        client = oauth.Client(consumer)
        resp, content = client.request(request_token_url, "GET", callback_url='http://localhost:8888/authentication/verify')
        if resp['status'] != '200':
            raise Exception("Invalid response %s:\n%s" % (resp['status'], content))

        request_token = self.get_token(content)
        authorize_url = usos_url + 'services/oauth/authorize'

        url_redirect = "%s?oauth_token=%s" % (authorize_url, request_token.key)
        self.redirect(url_redirect)


class VerifyHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        oauth_token = self.get_argument("oauth_token")
        oauth_verifier = self.get_argument("oauth_verifier")


        print '''
            TODO: zrob zapis/odczyt z bazy wzgledem, oauth_token, oauth_verifier
            jesli ok przekierowanie do odpowiedniej strony badz blad 400/500
            ''', oauth_token, oauth_verifier

        '''
        access_token_url = usos_url + 'services/oauth/access_token'

        request_token = self._read_token(content)
        request_token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, request_token)
            resp, content = client.request(access_token_url, "GET")
            try:
                access_token = self._read_token(content)
            except KeyError:
                print "Cound not retrieve Access Token (invalid outh_verifier)."
        '''

        self.write("See logs for details")


class TestHandler(BaseHandler, usosmixin.UsosMixin):

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("oauth_token", None):
            user = yield self.get_authenticated_user()
            # Save the user using e.g. set_secure_cookie()
            print "usos user authenticated", user
        else:
            yield self.authorize_redirect("/authentication/login")