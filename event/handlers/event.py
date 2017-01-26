# coding=UTF-8

import json
import logging
from datetime import datetime

from bson.objectid import ObjectId
from tornado import web
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop

from commons import utils
from commons.OneSignal import OneSignal
from commons.constants import fields, collections, config
from commons.context import Context
from commons.enumerators import ExceptionTypes
from commons.errors import EventError
from commons.handlers import AbstractHandler
from event.utils import constants
from event.utils import formatter


class EventHandler(AbstractHandler):
    EXCEPTION_TYPE = ExceptionTypes.EVENT.value

    @web.asynchronous
    async def get(self, usos_id, event_type):
        challenge = None
        try:
            mode = self.get_argument('hub.mode', default=None)
            challenge = self.get_argument('hub.challenge', default=None)
            verify_token = self.get_argument('hub.verify_token', default=None)

            logging.info(
                'usos_id {0} event_type {1} mode {2} challenge {3} verify_token {4}'.format(usos_id, event_type, mode,
                                                                                            challenge, verify_token))

            if not mode or not challenge or not verify_token:
                raise EventError('Required parameters not passed.')

            usos_doc = await self.db[collections.USOSINSTANCES].find_one({fields.USOS_ID: usos_id})

            if not usos_doc:
                raise EventError('Unknown usos_id: {0}'.format(usos_id))

            verify_token_doc = await self.db[collections.EVENTS_VERIFY_TOKENS].find_one(
                {fields.MONGO_ID: ObjectId(verify_token)})

            if not verify_token_doc:
                logging.debug('verify_token_doc: {0} usos_id: {1}'.format(verify_token_doc, usos_id))
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

    async def _updateStatus(self, event_id, status):
        await self.db[collections.EVENTS_USOS].update({fields.MONGO_ID: event_id},
                                                      {'$set': {fields.EVENT_STATUS: status}})

    async def _grader(self, grader_id, context):
        '''
            get grader data
        :param grader_id:
        :return:
        '''

        fields = 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'

        try:
            result = await context.usosCaller.call(path='services/users/user',
                                                   arguments={'fields': fields, 'user_id': grader_id})
            return result['first_name'] + ' ' + result['last_name']
        except Exception as ex:
            logging.exception(ex)
            return 'Nieznany'

    async def _one_signal(self, event_type, user_data, event_operation, user_doc, http_client):
        '''
            format notification and send to onesignal
        :return:
        '''

        logging.info('_one_signal event_type: {0} user_data: {1} event_operation: {2} email: {3}'.format(
            event_type, user_data, event_operation, user_doc[fields.USER_EMAIL]
        ))

        notification, message_title, message_body = None, None, None

        if event_type == constants.EVENT_TYPE_USER_POINT:
            notification, message_title, message_body = formatter.format_user_point(user_data,
                                                                                    event_operation)
        elif event_type == constants.EVENT_TYPE_USER_GRADE:
            notification, message_title, message_body = formatter.format_user_grade(user_data,
                                                                                    event_operation)
        if notification and message_title and message_body:
            onesignal_result = await OneSignal(self.config, http_client=http_client).signal_message(
                message=notification, email_reciepient=user_doc[fields.USER_EMAIL])

            logging.debug('onesignal_result {0}'.format(onesignal_result))

            message_doc = await self.db[collections.MESSAGES].insert({
                fields.USER_ID: user_doc[fields.MONGO_ID],
                fields.CREATED_TIME: datetime.now(),
                fields.FIELD_MESSAGE_FROM: message_title,
                fields.FIELD_MESSAGE_TYPE: 'powiadomienie',
                fields.ONESIGNAL_NOTIFICATION_TEXT: notification,
                fields.ONESIGNAL_NOTIFICATION_RESULT: onesignal_result,
            })

            logging.info('saved message_doc: {0}'.format(message_doc))

        else:
            return EventError('Błędnie przeprocesowane wysłanie wiadomosci OneSignal '
                              'notification: {0} message_title: {1} message_body: {2}'.format(
                notification, message_title, message_body
            ))

    async def _user_event(self, user_doc, node_id, event_type, event_operation, http_client):

        logging.debug(
            '_user_event: {0} {1} {2} {3}'.format(user_doc[fields.MONGO_ID], node_id, event_type, event_operation))

        usos_doc = await self.db_get_usos(user_doc[fields.USOS_ID])
        context = Context(self.config, user_doc=user_doc, usos_doc=usos_doc, http_client=http_client,
                          io_loop=IOLoop.current())

        if event_type == constants.EVENT_TYPE_USER_POINT:

            try:
                user_point = await context.usosCaller.call(path='services/crstests/user_point',
                                                           arguments={'node_id': node_id})

            except Exception as ex:
                logging.exception(ex)
                raise EventError('No notification for type: {0} {1}'.format(constants.EVENT_TYPE_USER_POINT,
                                                                            user_doc[fields.MONGO_ID]))

            logging.info('{0} user_point: {1}'.format(constants.EVENT_TYPE_USER_POINT, user_point))

            root_id_doc = await context.usosCaller.call(path='services/crstests/root_node',
                                                        arguments={'node_id': node_id, 'fields': 'root_id'})

            course_edition_doc = await context.usosCaller.call(path='services/crstests/root_node',
                                                               arguments={'node_id': root_id_doc['root_id'],
                                                                          'fields': 'course_edition'})

            logging.debug('{0} course_edition_doc: {1}'.format(constants.EVENT_TYPE_USER_POINT, course_edition_doc))

            user_point[fields.COURSE_NAME] = course_edition_doc[fields.COURSE_EDITION][fields.COURSE_NAME]
            user_point[constants.GRADER] = await self._grader(user_point['grader_id'], context)

            await self._one_signal(constants.EVENT_TYPE_USER_POINT, user_point, event_operation,
                                   user_doc, http_client)

        elif event_type == constants.EVENT_TYPE_USER_GRADE:

            try:
                user_grade = await context.usosCaller.call(path='services/crstests/user_grade',
                                                           arguments={'node_id': node_id})
            except Exception as ex:
                logging.exception(ex)
                raise EventError('No notification for type: {0} {1}'.format(constants.EVENT_TYPE_USER_GRADE,
                                                                            user_doc[fields.MONGO_ID]))

            logging.info('{0} user_grade: {1}'.format(constants.EVENT_TYPE_USER_GRADE, user_grade))

            root_id_doc = await context.usosCaller.call(path='services/crstests/root_node',
                                                        arguments={'node_id': node_id, 'fields': 'root_id'})

            course_edition_doc = await context.usosCaller.call(path='services/crstests/root_node',
                                                               arguments={'node_id': root_id_doc['root_id'],
                                                                          'fields': 'course_edition'})

            logging.debug('{0} course_edition_doc: {1}'.format(constants.EVENT_TYPE_USER_GRADE, course_edition_doc))

            user_grade[fields.COURSE_NAME] = course_edition_doc[fields.COURSE_EDITION][fields.COURSE_NAME]

            user_grade[constants.GRADER] = await self._grader(user_grade['grader_id'], context)

            await self._one_signal(constants.EVENT_TYPE_USER_GRADE, user_grade, event_operation,
                                   user_doc, http_client)
        else:
            raise EventError('nierozpoznany typ powiadomienia: {0}'.format(event_type))

    def _logException(self, exception):
        logging.exception(exception)
        if isinstance(exception, HTTPError):
            logging.error('code: {0} message: {1} body: {2} effective_url: {3}'.format(
                exception.code, exception.message, str(exception.response.body), exception.response.effective_url
            ))

    async def process_event(self, event_id):

        try:
            event_doc = await self.db[collections.EVENTS_USOS].find_one({fields.MONGO_ID: event_id})
            logging.info('processing event_doc: {0}'.format(event_doc))

            http_client = utils.http_client(self.config.PROXY_HOST, self.config.PROXY_PORT, io_loop=IOLoop.current())

            for entry in event_doc['entry']:
                for usos_user_id in entry['related_user_ids']:

                    try:
                        user_doc = await self.db[collections.USERS].find_one({
                            fields.USOS_ID: event_doc[fields.USOS_ID],
                            fields.USOS_PAIRED: True,
                            fields.USOS_USER_ID: usos_user_id})

                        if not user_doc:
                            raise EventError(
                                'Uzytkownik usos_user_id: {0} dla usos_id: {1} nie istnieje w Kujonie.'.format(
                                    usos_user_id, event_doc[fields.USOS_ID]
                                ))

                        await self._user_event(user_doc,
                                               entry['node_id'],
                                               event_doc['event_type'],
                                               entry['operation'],
                                               http_client)
                        await self._updateStatus(event_id, 'one signal send.')
                    except Exception as ex:
                        self._logException(ex)

        except Exception as ex:
            await self._updateStatus(event_id, 'processing failed')
            self._logException(ex)

    @web.asynchronous
    async def post(self, usos_id, event_type):
        try:
            usos_doc = await self.db[collections.USOSINSTANCES].find_one({fields.USOS_ID: usos_id})

            if not usos_doc:
                raise EventError('Unknown usos_id: {0}'.format(usos_id))

            body = self.request.body
            if isinstance(body, bytes):
                body = str(body, config.ENCODING)

            logging.debug('usos_id {0} event_type {1} body {2}'.format(usos_id, event_type, body))

            event_data = json.loads(body)
            event_data[fields.USOS_ID] = usos_id
            event_data[fields.EVENT_STATUS] = 'new'

            event_id = await self.db_insert(collections.EVENTS_USOS, event_data)
            logging.debug('processing event_id: {0} for event_data: {1}'.format(event_id, event_data))

            IOLoop.current().spawn_callback(self.process_event, event_id)

            self.success(data='event consumed')
        except EventError as ex:
            await self.exc(ex, log_db=False)
        except Exception as ex:
            logging.exception(self.request.body)
            await self.exc(ex)
