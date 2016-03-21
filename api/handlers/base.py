# coding=UTF-8

import urlparse

import oauth2 as oauth
import tornado.gen
from commons import handlers, constants, settings
from commons.mixins.JSendMixin import JSendMixin
from emailqueue.queues import MongoDbEmailQueue


class BaseHandler(handlers.CommonHandler, JSendMixin):

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

    _usoses = list()
    _usoses_encrypted = list()
    @tornado.gen.coroutine
    def get_usoses(self, show_encrypted):

        if not self._usoses or not self._usoses_encrypted:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find()
            while (yield cursor.fetch_next):
                usos_encrypted = cursor.next_object()
                usos_encrypted['logo'] = settings.DEPLOY_WEB + usos_encrypted['logo']
                usos = usos_encrypted.copy()
                usos = dict(self.aes.decrypt_usos(usos))

                self._usoses.append(usos)
                self._usoses_encrypted.append(usos_encrypted)
        if show_encrypted:
            raise tornado.gen.Return(self._usoses_encrypted)
        else:
            raise tornado.gen.Return(self._usoses)

    @tornado.gen.coroutine
    def get_usos(self, key, value):
        usoses = yield self.get_usoses(show_encrypted=False)

        for u in usoses:
            if u[key] == value:
                raise tornado.gen.Return(u)
        raise tornado.gen.Return(None)

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


class UsosesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        data = yield self.get_usoses(show_encrypted=True)

        self.success(data)
