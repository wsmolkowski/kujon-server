import json
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

    def _read_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr['oauth_token'], arr['oauth_token_secret'])


    def get(self):
        oauth_token = None
        oauth_verifier = None
        try:
            oauth_token = str(self.get_argument("oauth_token"))
            oauth_verifier = str(self.get_argument("oauth_verifier"))
        except Exception, ex:
            print ex

        if (oauth_token and oauth_verifier):
            # Step 3. Access Token
            request_token = _read_token(content)
            request_token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, request_token)
            resp, content = client.request(access_token_url, "GET")
            try:
                access_token = _read_token(content)
            except KeyError:
                print "Cound not retrieve Access Token (invalid outh_verifier)."

        self.render("create.html", title=settings.PROJECT_TITLE)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):


        usos = str(self.get_argument("usos"))
        usos = usos.strip("\\")
        # wybrac usosa na podstawie ID:
        try:
            u = json.loads(usos)
        except Exception, ex:
            print "blad porczas ladowania".format(ex)
        print "aa"
        usos2 = '[{"name": "Uniwersyst Warszawski", "url": "https://usosapps.uw.edu.pl/", "consumer_secret": "Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG", "contact": "dsksysadm@adm.uw.edu.pl", "usos_id": "UW", "_id": {"$oid": "569a02c83d78216688a90ebd"}, "consumer_key": "KBt6uWPWUekUzFtNTyY9"}, {"name": "Politechnika Swietokrzystka", "url": "https://api.usos.tu.kielce.pl/", "consumer_secret": "PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA", "contact": "d.walczyk@tu.kielce.pl", "usos_id": "PS", "_id": {"$oid": "569a02c83d78216688a90ebe"}, "consumer_key": "equujDB5ZLzTmPfcy2c2"}]'
        usos2 = json.loads(usos2)
        print usos2

        usosapi_base_url = usos2[0]['url']
        consumer_key = usos2[0]['consumer_key']
        consumer_secret = usos2[0]['consumer_secret']



        if not (usosapi_base_url and consumer_key and consumer_secret):
            print "Fill the settings first."
            self.render("")
            return
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        request_token_url = usosapi_base_url + 'services/oauth/request_token?scopes=studies|offline_access'
        authorize_url = usosapi_base_url + 'services/oauth/authorize'
        access_token_url = authorize_url + 'services/oauth/access_token'
        # Step 1. Request Token
        client = oauth.Client(consumer)
        resp, content = client.request(request_token_url, "GET", callback_url='http://localhost:8888/authentication/create')
        if resp['status'] != '200':
            raise Exception("Invalid response %s:\n%s" % (resp['status'], content))


        def _read_token(content):
            arr = dict(urlparse.parse_qsl(content))
            return oauth.Token(arr['oauth_token'], arr['oauth_token_secret'])


        request_token = _read_token(content)
        # Step 2. Obtain authorization
        print "Go to the following link in your browser:"
        print "%s?oauth_token=%s" % (authorize_url, request_token.key)
        url_redirect = "%s?oauth_token=%s" % (authorize_url, request_token.key)
        self.redirect(url_redirect)
        return

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

        # # response = self.fetch('/api/user?mobile_id={0}&usos_id={1}&access_token_key={&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        #
        # user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: access_token_secret,
        #                                          constants.ACCESS_TOKEN_KEY: access_token_key},
        #                                          constants.USER_PRESENT_KEYS)
        # if user_doc:
        #     print "user already exists {0}".format(user_doc)
        #     # TODO: ustawic wartosc cookie
        #     self.set_secure_cookie(constants.USER_SECURE_COOKIE, "wartosc coookie")
        #     self.redirect("/")
        #
        # else:
        #     print "login authentication failed for {0} and {1}".format(access_token_key, access_token_secret)
        #     print "creating user url: {0} consumer_key: {1} consumer_secret: {2} access_token_key: {3} access_token_secret: {4}  ".format(
        #         url, consumer_key, consumer_secret, access_token_key, access_token_secret
        #     )
        #     try:
        #         print url, consumer_key, consumer_secret, access_token_key, access_token_secret
        #         result = yield usosupdater.request_user_info(url, consumer_key, consumer_secret, access_token_key, access_token_secret)
        #
        #         result[constants.USOS_ID] = result.pop('id')
        #         #result[constants.MOBILE_ID] = parameters.mobile_id
        #         result[constants.ACCESS_TOKEN_SECRET] = access_token_secret
        #         result[constants.ACCESS_TOKEN_KEY] = access_token_key
        #         result[constants.CREATED_TIME] = datetime.now()
        #
        #         user_doc = yield motor.Op(self.db.users.insert, result)
        #
        #         print "saved new user in database: {0}".format(user_doc)
        #         self.redirect("/")
        #     except Exception, ex:
        #         data = {
        #                 'alert_message': "User creation fail failed for {0} and {1}".format(access_token_key, access_token_key),
        #                 'alert_exception': ex,
        #         }
        #         print ex
        #         self.render("create.html", title=settings.PROJECT_TITLE, **data)


class TestHandler(BaseHandler, usosmixin.UsosMixin):

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("oauth_token", None):
            user = yield self.get_authenticated_user()
            # Save the user using e.g. set_secure_cookie()
            print "usos user authenticated", user
        else:
            yield self.authorize_redirect("/authentication/login")