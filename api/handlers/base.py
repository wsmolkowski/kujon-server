# coding=UTF-8

import urlparse

import oauth2 as oauth
import tornado.gen
import tornado.web
from bson import json_util
from tornado import httpclient
from tornado.escape import json_decode

from commons import constants, settings, utils, decorators
from commons.AESCipher import AESCipher
from commons.mixins.JSendMixin import JSendMixin
from database import DatabaseHandler


class BaseHandler(DatabaseHandler, JSendMixin):
    _COOKIE_FIELDS = (constants.ID, constants.ACCESS_TOKEN_KEY, constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                      constants.USOS_PAIRED)

    def set_default_headers(self):
        if self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False) \
                and self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False):
            # mobile access
            self.set_header("Access-Control-Allow-Origin", "*")
            # self.set_header("Access-Control-Allow-Credentials", "false")
        else:
            # web client access
            self.set_header("Access-Control-Allow-Origin", settings.DEPLOY_WEB)
            self.set_header("Access-Control-Allow-Credentials", "true")

        # self.set_header("Access-Control-Allow-Origin", settings.DEPLOY_WEB)
        # self.set_header("Access-Control-Allow-Credentials", "true")

            # self.set_header("Access-Control-Allow-Methods", "GET,POST")  # "GET,PUT,POST,DELETE,OPTIONS"

    @staticmethod
    def get_auth_http_client():
        if settings.PROXY_URL and settings.PROXY_PORT:
            httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                                 defaults=dict(proxy_host=settings.PROXY_URL,
                                                               proxy_port=settings.PROXY_PORT,
                                                               validate_cert=False))

        return httpclient.AsyncHTTPClient()

    def get_current_user(self):
        cookie = self.get_secure_cookie(constants.KUJON_SECURE_COOKIE)
        if cookie:
            cookie = json_decode(cookie)
            return json_util.loads(cookie)

        header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
        header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

        if header_email and header_token:
            user_doc = self.dao[constants.COLLECTION_USERS].find_one({
                # constants.USOS_PAIRED: True,
                constants.USER_EMAIL: header_email,
                # constants.MOBI_TOKEN: header_token,
            }, (constants.ID, constants.ACCESS_TOKEN_KEY, constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                constants.USOS_PAIRED)
            )

            return user_doc

        return None

    def config_data(self):
        user = self.get_current_user()
        if user and constants.USOS_PAIRED in user.keys():
            usos_paired = user[constants.USOS_PAIRED]
        else:
            usos_paired = False

        return {
            'API_URL': settings.DEPLOY_API,
            'USOS_PAIRED': usos_paired,
            'USER_LOGGED': True if user else False
        }

    @property
    def oauth_parameters(self):
        return {
            'proxy_info': utils.get_proxy(),
        }

    _aes = None

    @property
    def aes(self):
        if not self._aes:
            self._aes = AESCipher()
        return self._aes

    _usoses = list()

    @tornado.gen.coroutine
    def get_usoses(self, showtokens):
        if not self._usoses:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
            while (yield cursor.fetch_next):
                usos = cursor.next_object()
                usos['logo'] = settings.DEPLOY_WEB + usos['logo']
                self._usoses.append(usos)
        if not showtokens:
            usoses = list(self._usoses)
            for usos in usoses:
                usos.pop("consumer_secret")
                usos.pop("consumer_key")
            raise tornado.gen.Return(usoses)
        else:
            raise tornado.gen.Return(self._usoses)

    @tornado.gen.coroutine
    def get_usos(self, key, value):
        usoses = yield self.get_usoses(showtokens=True)

        for u in usoses:
            if u[key] == value:
                raise tornado.gen.Return(u)
        raise tornado.gen.Return(None)

    @staticmethod
    def validate_usos(usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(400, "Usos {0} nie jest wspierany. Skontaktuj się z administratorem.".format(
                parameters.usos_id))

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    def reset_user_cookie(self, user_doc):
        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.set_secure_cookie(constants.KUJON_SECURE_COOKIE,
                               tornado.escape.json_encode(json_util.dumps(user_doc)),
                               constants.COOKIE_EXPIRES_DAYS)


class UsosesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = yield self.get_usoses(showtokens=False)
        self.success(data)


class DefaultErrorHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.fail('404 - Strona o podanym adresie nie istnieje.')


class ApplicationConfigHandler(BaseHandler):
    @decorators.extra_headers(cache_age=None)
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.success(data=self.config_data())
