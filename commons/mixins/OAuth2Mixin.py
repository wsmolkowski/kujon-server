# coding=UTF-8

from datetime import datetime

from tornado import gen
from tornado.auth import OAuthMixin

from commons import constants, settings, utils

try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3

try:
    import urllib.parse as urllib_parse  # py3
except ImportError:
    import urllib as urllib_parse  # py2


class OAuth2Mixin(OAuthMixin):
    _OAUTH_CALLBACK_URI = settings.DEPLOY_API + '/authentication/verify'
    _OAUTH_BASE_URL = None
    _OAUTH_REQUEST_TOKEN_URL = None
    _OAUTH_AUTHORIZE_URL = None
    _OAUTH_ACCESS_TOKEN_URL = None
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False
    _CONSUMER_TOKEN = None

    def get_auth_http_client(self):
        return utils.http_client()

    def _oauth_consumer_token(self):
        return self._CONSUMER_TOKEN

    def set_up(self, usos_doc):
        """

        :param usos_doc:
        :return:
        """

        self._CONSUMER_TOKEN = dict(key=usos_doc[constants.CONSUMER_KEY], secret=usos_doc[constants.CONSUMER_SECRET])
        self._OAUTH_BASE_URL = usos_doc[constants.USOS_URL]
        self._OAUTH_REQUEST_TOKEN_URL = '{0}services/oauth/request_token'.format(self._OAUTH_BASE_URL)
        self._OAUTH_AUTHORIZE_URL = '{0}services/oauth/authorize'.format(self._OAUTH_BASE_URL)
        self._OAUTH_ACCESS_TOKEN_URL = '{0}services/oauth/access_token'.format(self._OAUTH_BASE_URL)

    @gen.coroutine
    def _oauth_get_user_future(self, access_token):
        response = dict()
        response[constants.USOS_PAIRED] = True
        response[constants.ACCESS_TOKEN_SECRET] = access_token['secret']
        response[constants.ACCESS_TOKEN_KEY] = access_token['key']
        response[constants.UPDATE_TIME] = datetime.now()

        raise gen.Return(response)
