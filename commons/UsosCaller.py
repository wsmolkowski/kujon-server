# coding=UTF-8


from tornado import gen, escape
from tornado.auth import OAuthMixin
from tornado.httpclient import HTTPRequest

from commons import utils, constants
from commons.errors import CallerError

try:
    import urllib.parse as urllib_parse  # py3
except ImportError:
    import urllib as urllib_parse  # py2


class UsosCaller(OAuthMixin):
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False

    def __init__(self, context):
        self._context = context

    def _oauth_base_uri(self):
        return self._context.base_uri

    def _oauth_consumer_token(self):
        return self._context.consumer_token

    @staticmethod
    def get_auth_http_client():
        return utils.http_client()

    @gen.coroutine
    def call(self, path, arguments={}):

        arguments['lang'] = 'pl'

        url = self._oauth_base_uri() + path

        # Add the OAuth resource request signature if we have credentials
        oauth = self._oauth_request_parameters(url, self._context.access_token, arguments)
        arguments.update(oauth)

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        client = self.get_auth_http_client()

        response = yield client.fetch(HTTPRequest(url=url,
                                                  connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                                                  request_timeout=constants.HTTP_REQUEST_TIMEOUT))

        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            raise gen.Return(escape.json_decode(response.body))
        else:
            raise CallerError('Error code: {0} with body: {1} while fetching: {2}'.format(response.code,
                                                                                          response.body,
                                                                                          url))
