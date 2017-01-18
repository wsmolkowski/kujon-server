# coding=utf-8

import json
import logging
from datetime import datetime

import motor.motor_tornado
from tornado import escape
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.testing import gen_test

from commons import utils
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.constants import collections, config, fields
from commons.enumerators import Environment
from event.server import get_application
from event.utils import constants as events_constants
from tests.base import BaseTestClass

USER_DOC = {'access_token_secret': 'cjFPyKjDk5GNTcqpxeEsfWuhd9bLApbaw7ECfqHv',
            'access_token_key': 'VkyGQdtREPCvULQnQ4uF',
            'usos_user_id': '1279833',
            'user_created': datetime.now(),
            'name': 'dzizes dzizes',
            'created_time': datetime.now(),
            'update_time': datetime.now(),
            'email': 'testowy@gmail.com',
            'usos_id': 'DEMO',
            'usos_paired': True,
            'user_type': 'google',
            'google': {
                'picture': 'https://lh3.googleusercontent.com/-f7w-r4iF8DM/AAAAAAAAAAI/AAAAAAAALGo/GDUJeUaHtUo/photo.jpg',
                'email': 'testowy@gmail.com',
                'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImI5Njk3MmI4NjUwZDFjOGNhMmM1NDA0MzhlNGQ5MzUxNzY5ODk0MzIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6Ik83MkVjcGVrSVVPT2xGMWlIVXAxQUEiLCJhdWQiOiI4OTY3NjU3Njg2MjgtYjF0dXQ1ZzZoamluN2lpbjZobjRxbzhsdDNiNmlobHQuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTI1MjEwOTU0NjU0NTA5OTg1MTciLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXpwIjoiODk2NzY1NzY4NjI4LWIxdHV0NWc2aGppbjdpaW42aG40cW84bHQzYjZpaGx0LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiZW1haWwiOiJkeml6ZXM0NTFAZ21haWwuY29tIiwiaWF0IjoxNDcxODY3ODg3LCJleHAiOjE0NzE4NzE0ODd9.PwLfed8_52aydutvkREXHsBcaYHsF2U4E1UQEo5PdaAOE6aJigWqeh4v8GRtYy3IxDzja9j75rkbFP0Hch0elyIDUxrWS2lnDile5TYqiyoXGEfEw6ADvZVq8dVklbGYqg_H5G32tuLUERyleYBWYrPrjJGIRNlEoD2w-Cou2YeHysQl9GNKZl7vmS62HPClPF0jXDQGag_ziHAKBRxl5d4JwC4h3Sg4XunUdUsoq1Ey5F_rAzo5cggCOsQCpXcuSGGWc7YDCDCGBW5JsJsPv6mAi1jgepP5OETMGHC_yrXmQcjUJyctooKVRLRmaLNujlTe95ne-4v8psKOXH_nZQ',
                'access_token': 'ya29.CjBHA89EmKP6zkOMrW0K7a3INpF-oZjtyV02aAtwNhrNwqc0_hJM9XoQbuyTbOyCC3I',
                'token_type': 'Bearer',
                'name': 'testowy@gmail.com',
                'expires_in': datetime.now()},
            }


class EventTest(BaseTestClass):
    def get_app(self):
        return get_application(self.config)

    @classmethod
    def setUpClass(self):
        super(BaseTestClass, self).setUpClass()

        logging.info('Preparing tests for class: {0}'.format(self.__name__))
        self.config = Config(Environment.TESTS.value)

    def setUp(self):
        super(BaseTestClass, self).setUp()

        self.client = utils.http_client(proxy_host=self.config.PROXY_HOST,
                                        proxy_port=self.config.PROXY_PORT,
                                        io_loop=self.io_loop)

        # io_loop=self.io_loop
        client = motor.motor_tornado.MotorClient(self.config.MONGODB_URI, )
        self.db = client[self.config.MONGODB_NAME]
        logging.info(self.db)
        self.aes = AESCipher(self.config.AES_SECRET)

        # self._app = self.get_app()
        self._app.settings[config.APPLICATION_DB] = self.db
        self._app.settings[config.APPLICATION_CONFIG] = self.config
        self._app.settings[config.APPLICATION_AES] = self.aes

        self.prepareDatabase(self.config)
        self.insert_user(user_doc=USER_DOC)

    @gen_test(timeout=20)
    def testEventSubscribe(self):
        # assume
        challange = 'BKHeL7VXuPDttqDVzWne'
        event_type = events_constants.EVENT_TYPE_USER_POINT
        self.prepareDatabase(self.config)

        result = self.insert_user(user_doc=USER_DOC)

        verify_token = yield self.db[collections.EVENTS_VERIFY_TOKENS].insert({
            fields.USER_ID: result[0],
            fields.EVENT_TYPE: event_type,
            fields.CREATED_TIME: datetime.now()
        })

        verify_token = str(verify_token)

        event_url = '/{0}/{1}?hub.mode=subscribe&hub.challenge={2}&hub.verify_token={3}'.format(
            result[0], event_type.split('/')[-1], challange, verify_token)

        # when
        result = yield self.client.fetch(HTTPRequest(url=self.get_url(event_url), method='GET'))

        # then
        self.assertEquals(bytes(challange, encoding=config.ENCODING), result.body)

    @gen_test(timeout=20)
    def testProcessEventUserPoint(self):
        # assume
        challange = 'BKHeL7VXuPDttqDVzWne'
        event_type = events_constants.EVENT_TYPE_USER_POINT
        self.prepareDatabase(self.config)

        result = self.insert_user(user_doc=USER_DOC)

        # assume - not notification to get
        verify_token = yield self.db[collections.EVENTS_VERIFY_TOKENS].insert({
            fields.USER_ID: result[0],
            fields.EVENT_TYPE: event_type,
            fields.CREATED_TIME: datetime.now()
        })

        verify_token = str(verify_token)

        event = {
            'event_type': events_constants.EVENT_TYPE_USER_POINT,
            'entry': [
                {'node_id': 21123, 'related_user_ids': ['1279833'], 'operation': 'create', 'time': 1484646806},
                {'node_id': 21123, 'related_user_ids': ['1101468'], 'operation': 'create', 'time': 1484646806}]}

        event_url = '/{0}/{1}?hub.mode=subscribe&hub.challenge={2}&hub.verify_token={3}'.format(
            result[0], event_type.split('/')[-1], challange, verify_token)

        # when
        response = yield self.client.fetch(HTTPRequest(url=self.get_url(event_url),
                                                       headers=HTTPHeaders({
                                                           'Content-type': 'application/json',
                                                           'Accept': 'text/plain'}),
                                                       method='POST',
                                                       body=json.dumps(event)))

        # then
        result = escape.json_decode(response.body)
        self.assertEqual('event consumed', result['data'])

    @gen_test(timeout=20)
    def testProcessEventUserGrade(self):
        # assume
        challange = 'BKHeL7VXuPDttqDVzWne'
        event_type = events_constants.EVENT_TYPE_USER_GRADE
        self.prepareDatabase(self.config)

        result = self.insert_user(user_doc=USER_DOC)

        # assume - not notification to get
        verify_token = yield self.db[collections.EVENTS_VERIFY_TOKENS].insert({
            fields.USER_ID: result[0],
            fields.EVENT_TYPE: event_type,
            fields.CREATED_TIME: datetime.now()
        })

        verify_token = str(verify_token)

        event = {
            'event_type': events_constants.EVENT_TYPE_USER_GRADE,
            'entry': [{'node_id': 24614, 'related_user_ids': ['1279833'], 'operation': 'create', 'time': 1484643370}]}

        event_url = '/{0}/{1}?hub.mode=subscribe&hub.challenge={2}&hub.verify_token={3}'.format(
            result[0], event_type.split('/')[-1], challange, verify_token)

        # when
        response = yield self.client.fetch(HTTPRequest(url=self.get_url(event_url),
                                                       headers=HTTPHeaders({
                                                           'Content-type': 'application/json',
                                                           'Accept': 'text/plain'}),
                                                       method='POST',
                                                       body=json.dumps(event)))

        # then
        result = escape.json_decode(response.body)
        self.assertEqual('event consumed', result['data'])

    @gen_test(timeout=20)
    def testProcessEventFailureFakeVerifyToken(self):
        # assume
        challange = 'BKHeL7VXuPDttqDVzWne'
        event_type = events_constants.EVENT_TYPE_USER_GRADE
        self.prepareDatabase(self.config)

        result = self.insert_user(user_doc=USER_DOC)

        verify_token = yield self.db[collections.EVENTS_VERIFY_TOKENS].insert({
            fields.USER_ID: result[0],
            fields.EVENT_TYPE: event_type,
            fields.CREATED_TIME: datetime.now()
        })

        verify_token = str(verify_token)

        event_url = '/{0}/{1}?hub.mode=subscribe&hub.challenge={2}&hub.verify_token={3}'.format(
            result[0], event_type.split('/')[-1], challange, verify_token)

        # when
        result = yield self.client.fetch(HTTPRequest(url=self.get_url(event_url), method='GET'))

        # then
        self.assertEquals(bytes(challange, encoding=config.ENCODING), result.body)
