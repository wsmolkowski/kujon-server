# coding=UTF-8

import copy

from bson import json_util
from tornado import gen, web, escape
from tornado.escape import json_decode

from commons import constants, settings, utils
from commons.AESCipher import AESCipher
from commons.mixins.JSendMixin import JSendMixin
from database import DatabaseHandler


class BaseHandler(DatabaseHandler, JSendMixin):
    _COOKIE_FIELDS = (constants.ID, constants.ACCESS_TOKEN_KEY, constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                      constants.USOS_PAIRED, constants.USER_EMAIL)

    @gen.coroutine
    def prepare(self):
        if not hasattr(self, '_usoses') or not self._usoses:
            yield self.get_usoses(showtokens=True)

        user = None
        if hasattr(self, 'user_doc') and self.user_doc:
            user = self.user_doc

        if not user:
            cookie = self.get_secure_cookie(constants.KUJON_SECURE_COOKIE)
            if cookie:
                cookie = json_decode(cookie)
                user = json_util.loads(cookie)

        if not user:
            header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
            header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

            if header_email and header_token:
                token_exists = yield self.find_token(header_email)

                if token_exists:
                    user = yield self.db_current_user(header_email)

        self.current_user = user

    def set_default_headers(self):
        if self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False) \
                and self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False):
            # mobile access
            self.set_header("Access-Control-Allow-Origin", "*")
        else:
            # web client access
            self.set_header("Access-Control-Allow-Origin", settings.DEPLOY_WEB)
            self.set_header("Access-Control-Allow-Credentials", "true")

    @staticmethod
    def get_auth_http_client():
        return utils.http_client()

    def get_current_user(self):
        return self.current_user

    def config_data(self):
        user = self.get_current_user()
        if user and constants.USOS_PAIRED in user.keys():
            usos_paired = user[constants.USOS_PAIRED]
        else:
            usos_paired = False

        config = {
            'API_URL': settings.DEPLOY_API,
            'USOS_PAIRED': usos_paired,
            'USER_LOGGED': True if user else False
        }

        return config

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

    @gen.coroutine
    def get_usoses(self, showtokens):

        if not self._usoses:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})

            while (yield cursor.fetch_next):
                usos = cursor.next_object()
                usos['logo'] = settings.DEPLOY_WEB + usos['logo']

                if settings.ENCRYPT_USOSES_KEYS:
                    usos = dict(self.aes.decrypt_usos(usos))

                self._usoses.append(usos)

        result_usoses = copy.deepcopy(self._usoses)
        if not showtokens:
            for usos in result_usoses:
                usos.pop("consumer_secret")
                usos.pop("consumer_key")
                usos.pop("enabled")
                usos.pop("contact")
                usos.pop("url")
        raise gen.Return(result_usoses)

    @gen.coroutine
    def get_usos(self, key, value):
        usoses = yield self.get_usoses(showtokens=True)

        for u in usoses:
            if u[key] == value:
                raise gen.Return(u)
        raise gen.Return(None)

    def reset_user_cookie(self, user_doc):
        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.set_secure_cookie(constants.KUJON_SECURE_COOKIE, escape.json_encode(json_util.dumps(user_doc)),
                               domain=settings.SITE_DOMAIN)


class UsosesApi(BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        data = yield self.get_usoses(showtokens=False)
        self.success(data, cache_age=constants.SECONDS_1MONTH)


class DefaultErrorHandler(BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        self.fail(message='Strona o podanym adresie nie istnieje.', code=404)


class ApplicationConfigHandler(BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        self.success(data=self.config_data())
