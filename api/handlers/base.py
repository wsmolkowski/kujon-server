# coding=UTF-8

import logging

from bson import json_util
from tornado import gen, web, escape
from tornado.escape import json_decode
from tornado.util import ObjectDict
from tornado.web import RequestHandler

from commons import constants, settings, utils
from commons.AESCipher import AESCipher
from commons.mixins.ApiFriendsMixin import ApiMixinFriends
from commons.mixins.ApiMixin import ApiMixin
from commons.mixins.ApiSearchMixin import ApiMixinSearch
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.JSendMixin import JSendMixin


class BaseHandler(RequestHandler, DaoMixin):
    EXCEPTION_TYPE = 'base'

    @gen.coroutine
    def _prepare_user(self):
        user = None

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
                    logging.warning('Authentication token does not exists for email: {0}'.format(header_email))

                user = yield self.db_current_user(header_email)

        raise gen.Return(user)

    @gen.coroutine
    def prepare(self):
        self._context = ObjectDict()
        self._context.usoses = yield self.get_usos_instances()
        self._context.user_doc = yield self._prepare_user()

        if self._context.user_doc and constants.USOS_ID in self._context.user_doc:
            usos_id = self._context.user_doc[constants.USOS_ID]  # request authenticated
        else:
            usos_id = self.get_argument('usos_id', default=None)  # request authentication/register

        if usos_id:
            for usos in self._context.usoses:
                if usos[constants.USOS_ID] == usos_id:
                    self._context.usos_doc = usos

    def get_current_user(self):
        return self._context.user_doc

    def get_current_usos(self):
        return self._context.usos_doc

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

    def reset_user_cookie(self, user_doc):
        self.clear_cookie(constants.KUJON_SECURE_COOKIE)
        self.set_secure_cookie(constants.KUJON_SECURE_COOKIE, escape.json_encode(json_util.dumps(user_doc)),
                               domain=settings.SITE_DOMAIN)


class ApiHandler(BaseHandler, ApiMixin, ApiMixinFriends, ApiMixinSearch, JSendMixin):
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
        usoses = list()
        for usos in self._context.usoses:
            wanted_keys = [constants.USOS_LOGO, constants.USOS_ID, constants.USOS_NAME, constants.USOS_URL]
            usoses.append(dict((k, usos[k]) for k in wanted_keys if k in usos))

        self.success(usoses, cache_age=constants.SECONDS_1WEEK)


class DefaultErrorHandler(BaseHandler, JSendMixin):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        self.fail(message='Strona o podanym adresie nie istnieje.', code=404)


class ApplicationConfigHandler(BaseHandler, JSendMixin):
    """
        for mobile use only
    """

    @web.asynchronous
    @gen.coroutine
    def get(self):

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

        self.success(data=config)
