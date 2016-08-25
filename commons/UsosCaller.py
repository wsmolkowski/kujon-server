# coding=UTF-8

import urllib.parse as urllib_parse
from base64 import b64encode

from tornado import escape
from tornado.auth import OAuthMixin

from commons import utils
from commons.errors import CallerError


class UsosCaller(OAuthMixin):
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False

    def __init__(self, context=None):
        self._context = context

    def _oauth_base_uri(self):
        return self._context.base_uri

    def _oauth_consumer_token(self):
        return self._context.consumer_token

    async def call(self, path, arguments=None):
        if not arguments:
            arguments = dict()

        if arguments:
            arguments['lang'] = 'pl'

        url = self._oauth_base_uri() + path

        # Add the OAuth resource request signature if we have credentials
        oauth = self._oauth_request_parameters(url, self._context.access_token, arguments)
        arguments.update(oauth)

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        client = utils.http_client(self._context.proxy_url, self._context.proxy_port)
        response = await client.fetch(
            utils.http_request(url=url, proxy_url=self._context.proxy_url, proxy_port=self._context.proxy_port,
                               x_forwarded_for=self._context.remote_ip))

        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            return escape.json_decode(response.body)
        elif response.code == 200 and 'image/jpg' in response.headers['Content-Type']:
            return {'photo': b64encode(response.body)}
        else:
            raise CallerError('Error code: {0} with body: {1} while USOS fetching: {2}'.format(response.code,
                                                                                               response.body,
                                                                                               url))


class AsyncCaller(object):
    def __init__(self, context=None):
        self._context = context

    async def call_async(self, path, arguments=None, base_url=None, lang=True):
        if not arguments:
            arguments = dict()

        if lang:
            arguments['lang'] = 'pl'

        if not base_url:
            url = self._context.base_uri + path
        else:
            url = base_url + path

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        client = utils.http_client(self._context.proxy_url, self._context.proxy_port)
        response = await client.fetch(
            utils.http_request(url=url, proxy_url=self._context.proxy_url, proxy_port=self._context.proxy_port,
                               x_forwarded_for=self._context.remote_ip))

        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            return escape.json_decode(response.body)
        else:
            raise CallerError('Error code: {0} with body: {1} while async fetching: {2}'.format(response.code,
                                                                                                response.body,
                                                                                                url))
