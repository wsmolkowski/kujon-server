# coding=UTF-8

import json
import logging
from datetime import datetime

from bson import ObjectId
from tornado import web

from commons.constants import fields, collections, config
from commons.enumerators import ExceptionTypes
from commons.enumerators import JobStatus, JobType
from commons.errors import AuthenticationError
from commons.handlers import AbstractHandler


class EventHandler(AbstractHandler):
    SUPPORTED_METHODS = ('GET', 'POST')
    EXCEPTION_TYPE = ExceptionTypes.EVENT.value

    async def prepare(self):
        await super(EventHandler, self).prepare()

        verify_token = self.get_argument('hub.verify_token', default=None)
        if verify_token:
            verify_token = self.aes.decrypt(verify_token.encode()).decode()
            self._context.user_doc = await self.db[collections.USERS].find_one(
                {fields.MONGO_ID: ObjectId(verify_token)})
        else:
            self._context.user_doc = None

        header_hub_signature = self.request.headers.get(config.EVENT_X_HUB_SIGNATURE, False)
        logging.debug('header_hub_signature: {0}'.format(header_hub_signature))
        # X-Hub-Signature validation

    @web.asynchronous
    async def get(self, usos_id):
        try:
            self._context.usos_doc = await self.db_get_usos(usos_id)

            mode = self.get_argument('hub.mode', default=None)
            challenge = self.get_argument('hub.challenge', default=None)
            verify_token = self.get_argument('hub.verify_token', default=None)

            if not mode or not challenge or not verify_token:
                logging.error('Required parameters not passed.')
                self.error(code=400, message='Required parameters not passed.')
            else:
                # if not self.get_current_user():
                #     logging.error('Token verification failure for verify_token (user_id): {0}'.format(verify_token))
                #     self.fail(message='Token verification failure.')

                logging.debug('Event subscription verification ok for: mode:{0} challenge:{1} verify_token:{2}'.format(
                    mode, challenge, verify_token))

                self.write(challenge)
                self.finish()

        except Exception as ex:
            await self.exc(ex)

    @web.asynchronous
    async def post(self, usos_id):
        try:
            self._context.usos_doc = await self.db_get_usos(usos_id)

            if not self.getUsosId():
                raise AuthenticationError('Nieznany USOS {0}'.format(usos_id))

            body = self.request.body
            if isinstance(body, bytes):
                body = str(body, fields.ENCODING)

            event_data = json.loads(body)
            event_data[fields.USOS_ID] = self.getUsosId()

            await self.db_insert(collections.JOBS_QUEUE, {
                fields.CREATED_TIME: datetime.now(),
                fields.UPDATE_TIME: None,
                fields.JOB_MESSAGE: None,
                fields.JOB_DATA: event_data,
                fields.JOB_STATUS: JobStatus.PENDING.value,
                fields.JOB_TYPE: JobType.SUBSCRIPTION_EVENT.value
            })

            self.success(data='event consumed')
        except Exception as ex:
            logging.exception(self.request.body)
            await self.exc(ex)
