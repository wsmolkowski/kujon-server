# coding=utf-8

import json
import logging

from tornado import escape
from tornado import httpclient
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders

from commons import constants
from commons.errors import OneSignalError

SIGNAL_NOTIFICATION_URL = 'https://onesignal.com/api/v1/notifications'


def http_client(proxy_url=None, proxy_port=None):
    if proxy_url and proxy_port:
        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                             defaults=dict(proxy_host=proxy_url,
                                                           proxy_port=proxy_port,
                                                           validate_cert=False),
                                             max_clients=constants.MAX_HTTP_CLIENTS)

    else:
        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                             max_clients=constants.MAX_HTTP_CLIENTS)

    return httpclient.AsyncHTTPClient()


class OneSignalMixin(object):
    async def signal_fetch(self, fetch_url):
        client = http_client(self.config.PROXY_URL, self.config.PROXY_PORT)

        headers = HTTPHeaders({
            'Content-Type': 'application/json',
            'Authorization': self.config.AUTHORIZATION
        })

        response = await client.fetch(HTTPRequest(url=fetch_url,
                                                  use_gzip=True,
                                                  headers=headers,
                                                  connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                                                  request_timeout=constants.HTTP_REQUEST_TIMEOUT))

        logging.info('signal_fetch response code: {0} reason: {1}'.format(response.code, response.reason))
        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            return escape.json_decode(response.body)
        else:
            raise OneSignalError(
                'OneSignal response Error code: {0} with body: {1} while fetching: {2}'.format(response.code,
                                                                                               response.body,
                                                                                               fetch_url))

    async def signal_message(self, message, email_reciepient, language='en'):

        headers = HTTPHeaders({
            'Content-Type': 'application/json',
            'Authorization': self.config.SIGNAL_AUTHORIZATION
        })

        body = json.dumps({
            'app_id': self.config.APPLICATION_ID,
            'tags': [{"key": "user_email", "relation": "=", email_reciepient: "true"}],
            'contents': {language: message}
        })

        response = await self.get_auth_http_client().fetch(HTTPRequest(url=SIGNAL_NOTIFICATION_URL,
                                                                       method='POST',
                                                                       headers=headers,
                                                                       body=body,
                                                                       user_agent=self.config.PROJECT_TITLE,
                                                                       connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                                                                       request_timeout=constants.HTTP_REQUEST_TIMEOUT))

        logging.debug('signal_message response code: {0} reason: {1}'.format(response.code, response.reason))
        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            return escape.json_decode(response.body)
        else:
            raise OneSignalError('OneSignal response Error code: {0} with body: {1} '.format(response.code, body))
