import urlparse

import httplib2
import oauth2 as oauth
import tornado.gen
from bson import json_util
from httplib2 import socks
from tornado import httpclient
from tornado.web import RequestHandler

from usosapi import constants, settings
from usosapi.mixins.JSendMixin import JSendMixin
from usosweb import settings as usosweb_settings


class BaseHandler(RequestHandler, JSendMixin):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Origin", usosweb_settings.DEPLOY_URL)
        self.set_header("Access-Control-Allow-Credentials", "true")
        #self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")


    def get_auth_http_client(self):

        if settings.PROXY_URL and settings.PROXY_PORT:
            tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                                         defaults=dict(proxy_host=settings.PROXY_URL,
                                                                       proxy_port=settings.PROXY_PORT,
                                                                       validate_cert=False))

        return httpclient.AsyncHTTPClient()

    @property
    def oauth_parameters(self):
        return {
            'proxy_info': self.get_proxy(),
        }

    @property
    def crowler(self):
        return self.application.crowler

    @property
    def db(self):
        return self.application.db

    @tornado.gen.coroutine
    def get_parameters(self):

        user_doc = self.get_current_user()

        if not user_doc:
            usos_id = self.get_argument(constants.USOS_ID, default=None, strip=True)
            mobile_id = self.get_argument(constants.MOBILE_ID, default=None, strip=True)
            atk = self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True)
            ats = self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True)

            user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MOBILE_ID: mobile_id,
                                                                           constants.ACCESS_TOKEN_SECRET: atk,
                                                                           constants.ACCESS_TOKEN_KEY: ats})

        if not user_doc:
            raise tornado.web.HTTPError(500, "Request not authenticated")
            # self.error(message='Request not authenticated', code=501)

        raise tornado.gen.Return(user_doc)

    def get_current_user(self):
        cookie = self.get_secure_cookie(constants.USER_SECURE_COOKIE)
        if cookie:
            cookie = tornado.escape.json_decode(cookie)
            return json_util.loads(cookie)
        return None

    @staticmethod
    def validate_usos(usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(400,
                                        "Usos {0} not supported!".format(parameters.usos_id))

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    @staticmethod
    def get_proxy():
        if settings.PROXY_PORT and settings.PROXY_URL:
            return httplib2.ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host=settings.PROXY_URL, proxy_port=settings.PROXY_PORT, proxy_rdns=False)
        return None

    def template_data(self):
        usos_paired = False
        user = self.get_current_user()
        if user and constants.USOS_PAIRED in user.keys():
            usos_paired = user[constants.USOS_PAIRED]

        return {
            'PROJECT_TITLE': settings.PROJECT_TITLE,
            'DEPLOY_URL': settings.DEPLOY_URL,
            'USOS_PAIRED': usos_paired,
        }

    @tornado.gen.coroutine
    def get_usoses(self):
        usoses = []

        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find()
        while (yield cursor.fetch_next):
            usoses.append(cursor.next_object())

        raise tornado.gen.Return(usoses)

    @tornado.gen.coroutine
    def get_usos(self, usos_url):
        usoses = yield self.get_usoses()

        for u in usoses:
            if u['url'] == usos_url:
                raise tornado.gen.Return(u)
        raise tornado.gen.Return(None)


class UsosesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        #parameters = yield self.get_parameters()

        data = yield self.get_usoses()

        self.success(data)