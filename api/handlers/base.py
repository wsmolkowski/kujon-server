# coding=UTF-8

import urlparse

import oauth2 as oauth
import tornado.gen
from bson import json_util

from commons import handlers, constants
from commons.mixins.DatabaseMixin import DatabaseMixin
from commons.mixins.JSendMixin import JSendMixin


class BaseHandler(handlers.CommonHandler, DatabaseMixin, JSendMixin):
    _COOKIE_FIELDS = (constants.ID, constants.ACCESS_TOKEN_KEY, constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                      constants.USOS_PAIRED)

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

    @tornado.gen.coroutine
    def reset_user_cookie(self, user_doc=None):
        if not user_doc:
            user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: self.get_current_user()[constants.MONGO_ID]}, self._COOKIE_FIELDS)

        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.set_secure_cookie(constants.KUJON_SECURE_COOKIE,
                               tornado.escape.json_encode(json_util.dumps(user_doc)),
                               constants.COOKIE_EXPIRES_DAYS)


class UsosesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = yield self.get_usoses(show_encrypted=True)

        self.success(data)


class DefaultErrorHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.fail('Przepraszamy, ale strona o podanym adresie nie istnieje.')


class ApplicationConfigHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.success(data=self.config_data())
