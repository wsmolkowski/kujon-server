# coding=UTF-8

import urlparse

import oauth2 as oauth
import tornado.gen

from staraapi import settings
from staracommon import handlers, constants
from staracommon.mixins.JSendMixin import JSendMixin
from staraweb import settings as staraweb_settings


class BaseHandler(handlers.CommonHandler, JSendMixin):
    def set_default_headers(self):
        # self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Origin", staraweb_settings.DEPLOY_URL)
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "GET,POST")  # "GET,PUT,POST,DELETE,OPTIONS"

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
        if not user_doc or not user_doc['usos_paired']:
            raise tornado.web.HTTPError(400, "Request not authenticated..")

        raise tornado.gen.Return(user_doc)

    @staticmethod
    def validate_usos(usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(400, "Usos {0} not supported!".format(parameters.usos_id))

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    _usoses = []

    @tornado.gen.coroutine
    def get_usoses(self):

        if not self._usoses:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find()
            while (yield cursor.fetch_next):
                usos = cursor.next_object()
                usos['logo'] = settings.DEPLOY_URL + usos['logo']
                self._usoses.append(usos)

        raise tornado.gen.Return(self._usoses)

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
        # TODO: tutaj wylaczone jest sprawdzanie usera - czy na pewno tak ma zostac?
        # parameters = yield self.get_parameters()

        data = yield self.get_usoses()

        self.success(data)
