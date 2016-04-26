# coding=UTF-8

import json
import logging
from datetime import datetime

from bson.objectid import ObjectId
from tornado import gen
from tornado import web
from tornado.web import RequestHandler

from commons import constants
from commons.mixins.JSendMixin import JSendMixin


class MainHandler(RequestHandler, JSendMixin):
    SUPPORTED_METHODS = ('GET', 'POST')
    EXCEPTION_TYPE = 'event'

    @property
    def db(self):
        return self.application.db

    @gen.coroutine
    def user_exists(self, user_id):
        if isinstance(user_id, str) or isinstance(user_id, unicode):
            user_id = ObjectId(user_id)

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})
        if user_doc:
            raise gen.Return(True)
        else:
            raise gen.Return(False)

    @gen.coroutine
    def exc(self, exception):
        exc_doc = {
            'exception': str(exception)
        }

        if hasattr(self, 'argument_mode'):
            exc_doc['argument_mode'] = self.argument_mode
        if hasattr(self, 'argument_challenge'):
            exc_doc['argument_challenge'] = self.argument_challenge
        if hasattr(self, 'argument_mode'):
            exc_doc['argument_verify_token'] = self.argument_verify_token
        if hasattr(self, 'self.event_data'):
            exc_doc['event_data'] = self.event_data

        exc_doc[constants.EXCEPTION_TYPE] = self.EXCEPTION_TYPE
        exc_doc[constants.CREATED_TIME] = datetime.now()

        ex_id = yield self.db[constants.COLLECTION_EXCEPTIONS].insert(exc_doc)

        logging.debug(exc_doc)
        logging.error('handled exception {0} and saved in db with {1}'.format(exc_doc, ex_id))

        self.fail('Wystąpił błąd techniczny. Pracujemy nad rozwiązaniem.')

        raise gen.Return()

    @gen.coroutine
    def process_event(self, event_data):
        self.event_data = event_data

        logging.debug(self.event_data)
        logging.debug('entry: {0}'.format(self.event_data['entry']))
        logging.debug('event_type: {0}'.format(self.event_data['event_type']))

        raise gen.Return()


class EventHandler(MainHandler):
    # @web.asynchronous
    # def prepare(self):
    #     if not self.request.headers.get(constants.EVENT_X_HUB_SIGNATURE, False):
    #         self.fail('Required headers not passed.')
    #         return

    @web.asynchronous
    @gen.coroutine
    def post(self):
        try:
            event_data = json.loads(self.request.body)
            yield self.process_event(event_data)

            self.success(data='ok')
        except Exception, ex:
            yield self.exc(ex)


class VerifyHandler(MainHandler):
    @web.asynchronous
    def prepare(self):
        # if not self.request.headers.get(constants.EVENT_X_HUB_SIGNATURE, False):
        #    self.fail('Required headers not passed.')
        #    return

        mode = self.get_argument('hub.mode', default=None, strip=True)
        challenge = self.get_argument('hub.challenge', default=None, strip=True)
        verify_token = self.get_argument('hub.verify_token', default=None, strip=True)

        if not mode or not challenge or not verify_token:
            self.fail('Required parameters not passed.')
            return

        self.argument_mode = mode
        self.argument_challenge = challenge
        self.argument_verify_token = verify_token

        logging.debug('mode:{0} challenge:{1} verify_token:{2}'.format(
            self.argument_mode, self.argument_challenge, self.argument_verify_token))

    @web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            user_exists = yield self.user_exists(self.argument_verify_token)
            if not user_exists:
                self.fail('Token verification failure.')
                return

            logging.debug('token verification ok for: mode:{0} challenge:{1} verify_token:{2}'.format(
                self.argument_mode, self.argument_challenge, self.argument_verify_token))

            self.write(self.argument_challenge)
            self.finish()

        except Exception, ex:
            yield self.exc(ex)

    @web.asynchronous
    @gen.coroutine
    def post(self):
        try:
            event_data = json.loads(self.request.body)
            yield self.process_event(event_data)

            self.success(data='ok')
        except Exception, ex:
            yield self.exc(ex)

class DefaultErrorHandler(RequestHandler, JSendMixin):
    @web.asynchronous
    def get(self):
        self.error(message='Strona o podanym adresie nie istnieje.', code=401)
