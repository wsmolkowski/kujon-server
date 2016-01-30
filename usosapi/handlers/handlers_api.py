import urlparse

import tornado.web
from bson import json_util

import httplib2
import usosapi.oauth2 as oauth
from usosapi import constants, settings


class Parameters:
    def __init__(self, usos_id, mobile_id, user_id, access_token_key, access_token_secret):

        if not usos_id or not mobile_id or not access_token_key or not access_token_secret:
            raise tornado.web.HTTPError(400, "Given Parameters not supported.")

        self.usos_id = usos_id
        self.mobile_id = mobile_id
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret


class BaseHandler(tornado.web.RequestHandler):

    user_doc = None

    usos = None

    parameters = None

    @property
    def crowler(self):
        return self.application.crowler

    @property
    def db(self):
        return self.application.db

    @property
    def usoses(self):
        return self.application.usoses

    def get_current_user(self):
        cookie = self.get_secure_cookie(constants.USER_SECURE_COOKIE)
        if cookie:
            cookie = tornado.escape.json_decode(cookie)
            return json_util.loads(cookie)
        return None

    def get_parameters(self):

        user = self.get_current_user()
        try:
            if not user:
                return Parameters(
                        self.get_argument(constants.USOS_ID, default=None, strip=True),
                        self.get_argument(constants.MOBILE_ID, default=None, strip=True),
                        self.get_argument(constants.USER_ID, default=None, strip=True),
                        self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True),
                        self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True),
                )
            else:
                return Parameters(
                        user[constants.USOS_ID],
                        user[constants.MOBILE_ID],
                        user[constants.USER_ID],
                        user[constants.ACCESS_TOKEN_KEY],
                        user[constants.ACCESS_TOKEN_SECRET],
                )
        except Exception, ex:
            raise tornado.web.HTTPError(400,"Parameters not supported".format(ex.message))

    def validate_usos(self, usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(400,
                                        "Usos {0} not supported!".format(parameters.usos_id))

    def get_token(self, content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    def get_proxy(self):
        if settings.PROXY_PORT and settings.PROXY_URL:
            return httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP, settings.PROXY_URL, settings.PROXY_PORT)
        return None

    @staticmethod
    def template_data():
        return {
            'PROJECT_TITLE': settings.PROJECT_TITLE,
            'DEPLOY_URL': settings.DEPLOY_URL,
            constants.NEXT_PAGE: "/"
        }

    def get_usos(self, usos):
        for u in self.usoses:
            if u[constants.USOS_ID] == usos:
                return u
        return None
