# coding=UTF-8

import urlparse

import oauth2 as oauth
import tornado.gen
from bson import json_util
from emailqueue.queues import MongoDbEmailQueue

from commons import handlers, constants, settings
from commons.mixins.JSendMixin import JSendMixin


class BaseHandler(handlers.CommonHandler, JSendMixin):
    _COOKIE_FIELDS = (constants.ID, constants.ACCESS_TOKEN_KEY, constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                      constants.USOS_PAIRED)

    @property
    def crawler(self):
        return self.application.crawler

    @property
    def db(self):
        return self.application.db

    @tornado.gen.coroutine
    def get_parameters(self):

        user_doc = self.get_current_user()

        if not user_doc:
            # usos_id = self.get_argument(constants.USOS_ID, default=None, strip=True)
            # mobile_id = self.get_argument(constants.MOBILE_ID, default=None, strip=True)
            atk = self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True)
            ats = self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True)

            user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.ACCESS_TOKEN_SECRET: atk,
                                                                           constants.ACCESS_TOKEN_KEY: ats})
        if not user_doc or not user_doc['usos_paired']:
            raise tornado.gen.Return(self.fail("Request not authenticated."))

        raise tornado.gen.Return(user_doc)

    @staticmethod
    def validate_usos(usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(400, "Usos {0} not supported!".format(parameters.usos_id))

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    _email_queue = None

    @property
    def email_queue(self):
        if not self._email_queue:
            self._email_queue = MongoDbEmailQueue(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER,
                smtp_password=settings.SMTP_PASSWORD,
                mongodb_uri=settings.MONGODB_URI,
                mongodb_collection=constants.COLLECTION_EMAIL_QUEUE,
                mongodb_database=settings.MONGODB_NAME,
                queue_maxsize=0
            )
        return self._email_queue

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

        self.fail('Przepraszamy, ale podany adres nie istnieje.')


class ApplicationConfigHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()
        if user and constants.USOS_PAIRED in user.keys():
            usos_paired = user[constants.USOS_PAIRED]
        else:
            usos_paired = False

        self.success(data=self.config_data())