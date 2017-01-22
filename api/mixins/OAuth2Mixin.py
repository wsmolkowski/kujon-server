# coding=UTF-8

from datetime import datetime

from tornado import gen
from tornado.auth import OAuthMixin

from commons.constants import fields


class OAuth2Mixin(OAuthMixin):
    _OAUTH_CALLBACK_URI = None
    _OAUTH_BASE_URL = None
    _OAUTH_REQUEST_TOKEN_URL = None
    _OAUTH_AUTHORIZE_URL = None
    _OAUTH_ACCESS_TOKEN_URL = None
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False
    _CONSUMER_TOKEN = None

    def _oauth_consumer_token(self):
        return self._CONSUMER_TOKEN

    def oauth_set_up(self, usos_doc):
        """

        :param usos_doc:
        :return:
        """
        self._OAUTH_CALLBACK_URI = self.config.DEPLOY_API + '/authentication/verify'
        self._CONSUMER_TOKEN = dict(key=usos_doc[fields.CONSUMER_KEY], secret=usos_doc[fields.CONSUMER_SECRET])
        self._OAUTH_BASE_URL = usos_doc[fields.USOS_URL]
        self._OAUTH_REQUEST_TOKEN_URL = '{0}services/oauth/request_token'.format(self._OAUTH_BASE_URL)
        self._OAUTH_AUTHORIZE_URL = '{0}services/oauth/authorize'.format(self._OAUTH_BASE_URL)
        self._OAUTH_ACCESS_TOKEN_URL = '{0}services/oauth/access_token'.format(self._OAUTH_BASE_URL)

    @gen.coroutine
    def _oauth_get_user_future(self, access_token):
        response = dict()
        response[fields.USOS_PAIRED] = True
        response[fields.ACCESS_TOKEN_SECRET] = access_token['secret']
        response[fields.ACCESS_TOKEN_KEY] = access_token['key']
        response[fields.UPDATE_TIME] = datetime.now()

        raise gen.Return(response)
