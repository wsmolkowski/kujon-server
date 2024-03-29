# coding=UTF-8

import pycurl
import urllib.parse as urllib_parse
from base64 import b64encode

from tornado import escape
from tornado.auth import OAuthMixin

from commons import utils
from commons.errors import CallerError


def strip_english_language(data):
    def clean_list(array):
        new_list = []
        for a in array:
            if isinstance(a, dict):
                new_list.append(strip_english_language(a))
            elif isinstance(a, list):
                new_list.append(clean_list(a))
            else:
                new_list.append(a)
        return new_list

    if isinstance(data, list):
        return clean_list(data)

    if not isinstance(data, dict):
        return data

    '''
    recursively changes fields in dictionary
    from:
        "name": { "en": "Faculty of Education", "pl": "Wydzia\u0142 Pedagogiczny" }

    to:
        "name": "Wydzia\u0142 Pedagogiczny"

    :param input_dictionary:
    :return:
    '''
    for key, value in data.items():
        if isinstance(value, dict) and 'pl' in value and 'en' in value:
            data[key] = value['pl']
        elif isinstance(value, dict):
            data[key] = strip_english_language(value)
        elif isinstance(value, list):
            data[key] = clean_list(value)

    return data


class AbstractCaller(object):

    def _prepare_curl_callback(self, curl):
        curl.setopt(pycurl.FRESH_CONNECT, pycurl.FRESH_CONNECT)

    async def request_fetch(self, url):

        return await self.client.fetch(

            utils.http_request(url=url,
                               proxy_host=self.proxy_host,
                               proxy_port=self.proxy_port,
                               x_forwarded_for=self.remote_ip,
                               prepare_curl_callback=self.prepare_curl_callback))

    async def _usos_response(self, response, url):
        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            if response.body == b'null':
                raise CallerError(
                    'Null USOS response: {0} with body: {1} while USOS fetching: {2}'.format(response.code,
                                                                                             response.body,
                                                                                             url))
            return strip_english_language(escape.json_decode(response.body))
        elif response.code == 200 and 'image/jpg' in response.headers['Content-Type']:
            return {'photo': b64encode(response.body)}
        else:
            raise CallerError('Error code: {0} with body: {1} while USOS fetching: {2}'.format(response.code,
                                                                                               response.body,
                                                                                               url))


class UsosCaller(AbstractCaller, OAuthMixin):
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False

    def __init__(self, base_uri, client, proxy_host, proxy_port, remote_ip, consumer_token, access_token,
                 prepare_curl_callback=None):
        self.base_uri = base_uri
        self.client = client
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.remote_ip = remote_ip
        self.consumer_token = consumer_token
        self.access_token = access_token

        if prepare_curl_callback:
            self.prepare_curl_callback = self._prepare_curl_callback
        else:
            self.prepare_curl_callback = None

    def _oauth_base_uri(self):
        return self.base_uri

    def _oauth_consumer_token(self):
        return self.consumer_token

    async def call(self, path, arguments=None):
        if not arguments:
            arguments = dict()

        if arguments:
            arguments['lang'] = 'pl'

        url = self._oauth_base_uri() + path

        # Add the OAuth resource request signature if we have credentials
        oauth = self._oauth_request_parameters(url, self.access_token, arguments)
        arguments.update(oauth)

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        response = await self.request_fetch(url)

        return await self._usos_response(response, url)


class AsyncCaller(AbstractCaller):
    def __init__(self, base_uri, client, proxy_host, proxy_port, remote_ip, prepare_curl_callback=None):
        self.base_uri = base_uri
        self.client = client
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.remote_ip = remote_ip

        if prepare_curl_callback:
            self.prepare_curl_callback = self._prepare_curl_callback
        else:
            self.prepare_curl_callback = None


    async def call_async(self, path, arguments=None, base_url=None, lang=True):
        if not arguments:
            arguments = dict()

        if lang:
            arguments['lang'] = 'pl'

        if not base_url:
            url = self.base_uri + path
        else:
            url = base_url + path

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        response = await self.request_fetch(url)

        return await self._usos_response(response, url)
