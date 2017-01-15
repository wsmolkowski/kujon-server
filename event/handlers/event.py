# coding=UTF-8

import json
import logging

from tornado import web
from tornado.ioloop import IOLoop

from commons.constants import collections, fields, config
from commons.errors import EventError
from event.handlers.abstract import EventAbstractHandler


class EventHandler(EventAbstractHandler):
    @web.asynchronous
    async def get(self, usos_id, user_usos_id):
        try:
            await self._buildContext(usos_id, user_usos_id)

            mode = self.get_argument('hub.mode', default=None)
            challenge = self.get_argument('hub.challenge', default=None)
            verify_token = self.get_argument('hub.verify_token', default=None)

            if not mode or not challenge or not verify_token:
                raise EventError('Required parameters not passed.')
            else:
                # if not self.get_current_user():
                #     logging.error('Token verification failure for verify_token (user_id): {0}'.format(verify_token))
                #     self.fail(message='Token verification failure.')

                logging.debug('Event subscription verification ok for: mode:{0} challenge:{1} verify_token:{2}'.format(
                    mode, challenge, verify_token))

                self.write(challenge)
                self.finish()
        except EventError as ex:
            await self.exc(ex, log_db=False)
        except Exception as ex:
            await self.exc(ex)

    @web.asynchronous
    async def post(self, usos_id, user_usos_id):
        try:
            await self._buildContext(usos_id, user_usos_id)

            body = self.request.body
            if isinstance(body, bytes):
                body = str(body, config.ENCODING)

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
