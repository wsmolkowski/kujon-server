# coding=UTF-8

import json
import logging

from bson import ObjectId
from tornado import web
from tornado.ioloop import IOLoop

from commons.constants import collections, fields, config
from commons.errors import EventError
from event.handlers.abstract import EventAbstractHandler


class EventHandler(EventAbstractHandler):
    @web.asynchronous
    async def get(self, user_id, event_type):
        challenge = None
        try:
            mode = self.get_argument('hub.mode', default=None)
            challenge = self.get_argument('hub.challenge', default=None)
            verify_token = self.get_argument('hub.verify_token', default=None)

            logging.debug(
                'user_id {0} event_type {1} mode {2} challenge {3} verify_token {4}'.format(user_id, event_type, mode,
                                                                                            challenge, verify_token))

            await self._buildContext(user_id)

            if not mode or not challenge or not verify_token:
                raise EventError('Required parameters not passed.')

            verify_token_doc = await self.db[collections.EVENTS_VERIFY_TOKENS].find_one(
                {fields.MONGO_ID: ObjectId(verify_token)})

            # or str(verify_token_doc[fields.USER_ID]) != str(self.getUserId())
            if not verify_token_doc:
                logging.debug('verify_token_doc: {0} user_id: {1}'.format(verify_token_doc, self.getUserId()))
                raise EventError('Required parameters not valid.')

            logging.debug('Event subscription verification ok for: mode:{0} challenge:{1} verify_token:{2}'.format(
                mode, challenge, verify_token))

        except EventError as ex:
            await self.exc(ex, log_db=False, finish=False)
        except Exception as ex:
            await self.exc(ex, finish=False)
        finally:
            self.write(challenge)
            self.finish()

    @web.asynchronous
    async def post(self, user_id, event_type):
        try:
            await self._buildContext(user_id)

            body = self.request.body
            if isinstance(body, bytes):
                body = str(body, config.ENCODING)

            logging.debug('user_id {0} event_type {1} body {2}'.format(user_id, event_type, body))

            event_data = json.loads(body)
            event_data[fields.USOS_ID] = self.getUsosId()
            event_data[fields.USER_ID] = self.getUserId()

            IOLoop.current().spawn_callback(self.db_insert, collections.EVENTS_USOS, event_data)
            IOLoop.current().spawn_callback(self.process_event, event_data)

            self.success(data='event consumed')
        except EventError as ex:
            await self.exc(ex, log_db=False)
        except Exception as ex:
            logging.exception(self.request.body)
            await self.exc(ex)
