# coding=UTF-8

import json
import logging
import traceback
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
        return self.application.settings['db']

    @gen.coroutine
    def user_exists(self, user_id):
        if isinstance(user_id, str) or isinstance(user_id, unicode):
            user_id = ObjectId(user_id)

        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})
        gen.Return(user_doc)

    @gen.coroutine
    def exc(self, exception):
        exc_doc = {
            'exception': str(exception)
        }
        exc_doc[constants.TRACEBACK] = traceback.format_exc()
        exc_doc[constants.EXCEPTION_TYPE] = self.EXCEPTION_TYPE
        exc_doc[constants.CREATED_TIME] = datetime.now()

        ex_id = yield self.db[constants.COLLECTION_EXCEPTIONS].insert(exc_doc)

        logging.exception(exception)
        logging.error('handled exception {0} and saved in db with {1}'.format(exc_doc, ex_id))

        self.fail(message='Wystąpił błąd techniczny. Pracujemy nad rozwiązaniem.')

    @gen.coroutine
    def process_event(self, event_data):
        self.event_data = event_data

        logging.debug(self.event_data)
        logging.debug('entry: {0}'.format(self.event_data['entry']))
        logging.debug('event_type: {0}'.format(self.event_data['event_type']))

        raise gen.Return()


class EventHandler(MainHandler):
    @gen.coroutine
    @web.asynchronous
    def prepare(self):
        header_hub_signature = self.request.headers.get(constants.EVENT_X_HUB_SIGNATURE, False)
        logging.debug('header_hub_signature: {0}'.format(header_hub_signature))

    @web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            mode = self.get_argument('hub.mode', default=None)
            challenge = self.get_argument('hub.challenge', default=None)
            verify_token = self.get_argument('hub.verify_token', default=None)

            if not mode or not challenge or not verify_token:
                logging.error('Required parameters not passed.')
                self.error(code=400, message='Required parameters not passed.')
            else:
                # enable for production :)
                # user_exists = yield self.user_exists(verify_token)
                # if not user_exists:
                #    logging.error('Token verification failure for verify_token: {0}'.format(self.argument_verify_token))
                #    self.fail(message='Token verification failure.')

                logging.debug('Event subscription verification ok for: mode:{0} challenge:{1} verify_token:{2}'.format(
                    mode, challenge, verify_token))

                self.write(challenge)
                self.finish()

        except Exception as ex:
            yield self.exc(ex)

    @web.asynchronous
    @gen.coroutine
    def post(self):
        try:
            event_data = json.loads(self.request.body)
            yield self.process_event(event_data)

            self.success(data='ok')
        except Exception as ex:
            yield self.exc(ex)


class DefaultErrorHandler(RequestHandler, JSendMixin):
    @web.asynchronous
    def get(self):
        self.error(message='Strona o podanym adresie nie istnieje.', code=401)
