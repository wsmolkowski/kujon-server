# coding=utf-8

import json
import logging

from tornado import escape
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders

from commons import utils
from commons.constants import config as application_config
from commons.errors import OneSignalError

SIGNAL_NOTIFICATION_URL = 'https://onesignal.com/api/v1/notifications'


class OneSignalMixin(object):
    async def signal_fetch(self, fetch_url):
        client = utils.http_client(self.config.PROXY_URL, self.config.PROXY_PORT)

        headers = HTTPHeaders({
            'Content-Type': 'application/json',
            'Authorization': self.config.AUTHORIZATION
        })

        response = await client.fetch(utils.http_request(url=fetch_url,
                                                         decompress_response=True,
                                                         headers=headers,
                                                         proxy_url=self.config.PROXY_URL,
                                                         proxy_port=self.config.PROXY_PORT))

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
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': self.config.AUTHORIZATION
        })

        body = json.dumps({
            'app_id': self.config.APPLICATION_ID,
            'filters': [
                {"field": "tag", "key": "user_email", "relation": "=", "value": email_reciepient},
            ],
            'contents': {language: message}
        })

        response = await self.get_auth_http_client().fetch(HTTPRequest(url=SIGNAL_NOTIFICATION_URL,
                                                                       method='POST',
                                                                       headers=headers,
                                                                       body=body,
                                                                       user_agent=self.config.PROJECT_TITLE,
                                                                       connect_timeout=application_config.HTTP_CONNECT_TIMEOUT,
                                                                       request_timeout=application_config.HTTP_REQUEST_TIMEOUT,
                                                                       proxy_host=self.config.PROXY_URL,
                                                                       proxy_port=self.config.PROXY_PORT
                                                                       ))

        logging.debug('signal_message response code: {0} reason: {1}'.format(response.code, response.reason))
        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            return escape.json_decode(response.body)
        else:
            raise OneSignalError('OneSignal response Error code: {0} with body: {1} '.format(response.code, body))
