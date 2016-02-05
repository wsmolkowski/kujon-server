import urlparse

import httplib2
import oauth2 as oauth
import tornado.web
from bson import json_util
from httplib2 import socks

from usosapi import constants, settings


class BaseHandler(tornado.web.RequestHandler):
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

            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: mobile_id,
                                                     constants.ACCESS_TOKEN_SECRET: atk,
                                                     constants.ACCESS_TOKEN_KEY: ats})

        if not user_doc:
            raise tornado.web.HTTPError(500, "Request not authenticated")

        usos_doc = yield self.get_usos(user_doc[constants.USOS_ID])

        raise tornado.gen.Return((user_doc, usos_doc))

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
            return httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, settings.PROXY_URL, settings.PROXY_PORT)
        return None

    @staticmethod
    def template_data():
        return {
            'PROJECT_TITLE': settings.PROJECT_TITLE,
            'DEPLOY_URL': settings.DEPLOY_URL,
            constants.NEXT_PAGE: "/"
        }

    @tornado.gen.coroutine
    def get_usoses(self):
        usoses = []

        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find()
        while (yield cursor.fetch_next):
            usoses.append(cursor.next_object())

        raise tornado.gen.Return(usoses)

    @tornado.gen.coroutine
    def get_usos(self, usos):
        usoses = yield self.get_usoses()

        for u in usoses:
            if u[constants.USOS_ID] == usos:
                raise tornado.gen.Return(u)
        raise tornado.gen.Return(None)
