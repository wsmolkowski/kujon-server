# coding=utf-8

import json
import logging

from tornado import gen
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders

from commons import utils, settings, constants

SIGNAL_NOTIFICATION_URL = 'https://onesignal.com/api/v1/notifications'


class OneSignalMixin(object):
    @gen.coroutine
    def signal_fetch(fetch_url):
        client = utils.http_client()

        headers = HTTPHeaders({
            'Content-Type': 'application/json',
            'Authorization': settings.AUTHORIZATION
        })

        response = yield client.fetch(HTTPRequest(url=fetch_url,
                                                  use_gzip=True,
                                                  headers=headers,
                                                  connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                                                  request_timeout=constants.HTTP_REQUEST_TIMEOUT))

        logging.info('response code: {0} reason: {1}'.format(response.code, response.reason))
        response_body = json.loads(response.body.decode(constants.ENCODING))

        raise gen.Return(response_body)

    @gen.coroutine
    def signal_message(message, email_reciepient, language='en'):
        client = utils.http_client()

        headers = HTTPHeaders({
            'Content-Type': 'application/json',
            'Authorization': settings.SIGNAL_AUTHORIZATION
        })

        body = json.dumps({
            'app_id': settings.APPLICATION_ID,
            # 'included_segments': ['All'],
            'include_player_ids': ['8bf236a8-83c9-4bfc-96e0-035cbc657b6d'],
            # 'tags': [{'user_email': email_reciepient}],
            # 'id': '5842429a-248d-4e73-8727-bdb8468ddaac',
            'contents': {language: message}
        })

        response = yield client.fetch(HTTPRequest(url=SIGNAL_NOTIFICATION_URL,
                                                  method='POST',
                                                  headers=headers,
                                                  body=body,
                                                  use_gzip=True,
                                                  connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                                                  request_timeout=constants.HTTP_REQUEST_TIMEOUT))

        logging.info('response code: {0} reason: {1}'.format(response.code, response.reason))
        response_body = json.loads(response.body.decode(constants.ENCODING))

        raise gen.Return(response_body)
