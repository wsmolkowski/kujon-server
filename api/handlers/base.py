# coding=UTF-8

import copy
import logging
from datetime import datetime

from bson import json_util
from tornado import gen, web, escape
from tornado.escape import json_decode
from tornado.web import RequestHandler

from commons import constants, settings, utils
from commons.AESCipher import AESCipher
from commons.mixins.ApiFriendsMixin import ApiMixinFriends
from commons.mixins.ApiMixin import ApiMixin
from commons.mixins.ApiSearchMixin import ApiMixinSearch
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.JSendMixin import JSendMixin
from crawler import email_factory


class BaseHandler(RequestHandler, DaoMixin):
    EXCEPTION_TYPE = 'base'

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
                token_exists = yield self.db_find_token(header_email)

                if not token_exists:
                    logging.warning('google token does not exists for email: {0}'.format(header_email))

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
            self._usoses = yield self.get_usos_instances()

        result_usoses = copy.deepcopy(self._usoses)
        usoses = list()
        if not showtokens:
            for usos in result_usoses:
                wanted_keys = ['logo', constants.USOS_ID, 'name']
                usoses.append(dict((k, usos[k]) for k in wanted_keys if k in usos))
        raise gen.Return(usoses)

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

    @gen.coroutine
    def db_email_registration(self, user_doc):

        usos_doc = yield self.get_usos(constants.USOS_ID, user_doc[constants.USOS_ID])
        recipient = user_doc[constants.USER_EMAIL]

        email_job = email_factory.email_job(
            'Rejestracja w Kujon.mobi',
            settings.SMTP_EMAIL,
            recipient if type(recipient) is list else [recipient],
            '\nCześć,\n'
            '\nRejestracja Twojego konta i połączenie z {0} zakończona pomyślnie.\n'
            '\nW razie pytań lub pomysłów na zmianę - napisz do nas.. dzięki Tobie Kujon będzie lepszy..\n'
            '\nPozdrawiamy,'
            '\nzespół Kujon.mobi'
            '\nemail: {1}\n'.format(usos_doc['name'], settings.SMTP_EMAIL)
        )

        yield self.db_insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

    @gen.coroutine
    def on_finish(self):
        user_doc = self.get_current_user()
        user_id = user_doc[constants.MONGO_ID] if user_doc else None

        yield self.db_insert(constants.COLLECTION_REQUEST_LOG, {
            'type': 'api',
            constants.USER_ID: user_id,
            constants.CREATED_TIME: datetime.now(),
            'host': self.request.host,
            'method': self.request.method,
            'path': self.request.path,
            'query': self.request.query,
            'remote_ip': self.request.remote_ip,
        })


class ApiHandler(BaseHandler, ApiMixin, ApiMixinFriends, ApiMixinSearch, JSendMixin):

    def data_received(self, chunk):
        super

    def _oauth_get_user(self, access_token, callback):
        super

    EXCEPTION_TYPE = 'api'

    def do_refresh(self):  # overwrite from ApiMixin
        if self.request.headers.get(constants.MOBILE_X_HEADER_REFRESH, False):
            return True
        return False

    _db = None

    @property
    def db(self):
        return self.application.settings['db']


class UsosesApi(BaseHandler, JSendMixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        data = yield self.get_usoses(showtokens=False)
        self.success(data, cache_age=constants.SECONDS_1MONTH)


class DefaultErrorHandler(BaseHandler, JSendMixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        self.fail(message='Strona o podanym adresie nie istnieje.', code=404)


class ApplicationConfigHandler(BaseHandler, JSendMixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        self.success(data=self.config_data())
