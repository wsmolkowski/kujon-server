# coding=UTF-8

import json
import logging
from datetime import datetime

from tornado import web

from commons import constants
from commons.enumerators import ExceptionTypes
from commons.enumerators import JobStatus, JobType
from commons.errors import AuthenticationError
from commons.handlers import AbstractHandler


class EventHandler(AbstractHandler):
    SUPPORTED_METHODS = ('GET', 'POST')
    EXCEPTION_TYPE = ExceptionTypes.EVENT.value

    @web.asynchronous
    async def prepare(self):
        header_hub_signature = self.request.headers.get(constants.EVENT_X_HUB_SIGNATURE, False)
        logging.debug('header_hub_signature: {0}'.format(header_hub_signature))
        # X-Hub-Signature validation

    @web.asynchronous
    async def get(self, usos_id):
        try:
            self.usos_id = usos_id

            mode = self.get_argument('hub.mode', default=None)
            challenge = self.get_argument('hub.challenge', default=None)
            verify_token = self.get_argument('hub.verify_token', default=None)

            if not mode or not challenge or not verify_token:
                logging.error('Required parameters not passed.')
                self.error(code=400, message='Required parameters not passed.')
            else:
                # verify_token = self.aes.decrypt(verify_token.encode()).decode()
                # user_exists = await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(verify_token)})
                #
                # if not user_exists:
                #     logging.error('Token verification failure for verify_token (user_id): {0}'.format(verify_token))
                #    self.fail(message='Token verification failure.')

                logging.debug('Event subscription verification ok for: mode:{0} challenge:{1} verify_token:{2}'.format(
                    mode, challenge, verify_token))

                self.write(challenge)
                self.finish()

        except Exception as ex:
            await self.exc(ex)

    @web.asynchronous
    async def post(self, usos_id):
        try:
            usos_doc = await self.db_get_usos(usos_id)

            if not usos_doc:
                raise AuthenticationError('Nieznany USOS {0}'.format(usos_id))

            event_data = json.loads(self.request.body)
            event_data[constants.USOS_ID] = usos_doc[constants.USOS_ID]

            await self.db_insert(constants.COLLECTION_JOBS_QUEUE, {
                constants.CREATED_TIME: datetime.now(),
                constants.UPDATE_TIME: None,
                constants.JOB_MESSAGE: None,
                constants.JOB_DATA: event_data,
                constants.JOB_STATUS: JobStatus.PENDING.value,
                constants.JOB_TYPE: JobType.SUBSCRIPTION_EVENT.value
            })

            self.success(data='event consumed')
        except Exception as ex:
            await self.exc(ex)
