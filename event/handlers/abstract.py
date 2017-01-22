# coding=UTF-8

import logging

from bson.objectid import ObjectId, InvalidId

from commons.constants import fields, collections, config
from commons.context import Context
from commons.enumerators import ExceptionTypes
from commons.errors import EventError
from commons.handlers import AbstractHandler
from event.utils import constants
from event.utils import formatter


class EventAbstractHandler(AbstractHandler):
    EXCEPTION_TYPE = ExceptionTypes.EVENT.value

    async def prepare(self):

        verify_token = self.get_argument('hub.verify_token', default=None)
        if verify_token:
            try:
                verify_token_doc = await self.db[collections.EVENTS_VERIFY_TOKENS].find_one(
                    {fields.MONGO_ID: ObjectId(verify_token)})
                if not verify_token_doc:
                    raise EventError('Wrong parameter verify_token.')

            except InvalidId as ex:
                raise EventError(str(ex))

            user_doc = await self.db[collections.USERS].find_one(
                {fields.MONGO_ID: verify_token_doc[fields.USER_ID]})

            if not user_doc:
                raise EventError('Unknown user for given verify_token.')

            usos_doc = await self.db_get_usos(user_doc[fields.USOS_ID])
            self._context = Context(self.config, user_doc=user_doc, usos_doc=usos_doc)
        else:
            self._context = Context(self.config)

        header_hub_signature = self.request.headers.get(config.EVENT_X_HUB_SIGNATURE, False)
        logging.debug('header_hub_signature: {0}'.format(header_hub_signature))
        # X-Hub-Signature validation

    async def _buildContext(self, user_id):

        user_doc = await self.db[collections.USERS].find_one({fields.MONGO_ID: ObjectId(user_id)})
        if not user_doc:
            raise EventError('Nierozpoznany użytkownik na podstawie podanych danych.')

        usos_doc = await self.db_get_usos(user_doc[fields.USOS_ID])
        self._context = Context(self.config, user_doc=user_doc, usos_doc=usos_doc)
        self._context.settings = await self.db_settings(self.getUserId())

    async def _updateStatus(self, event_id, status):
        await self.db[collections.EVENTS_USOS].update({fields.MONGO_ID: event_id},
                                                      {'$set': {fields.EVENT_STATUS: status}})

    async def _grader(self, grader_id):
        '''
            get grader data
        :param grader_id:
        :return:
        '''

        grader_doc = await self.api_user_info(grader_id)
        return grader_doc['first_name'] + ' ' + grader_doc['last_name']

    async def _one_signal(self, event_type, user_data, event_operation, email):
        '''
            format notification and send to onesignal
        :return:
        '''

        logging.info('_one_signal event_type: {0} user_data: {1} event_operation: {2} email: {3}'.format(
            event_type, user_data, event_operation, email
        ))

        notification, message_title, message_body = None, None, None

        if event_type == constants.EVENT_TYPE_USER_POINT:

            notification, message_title, message_body = formatter.format_user_point(user_data,
                                                                                    event_operation)
            onesignal_result = await self._osm.signal_message(message=notification,
                                                              email_reciepient=email)

        elif event_type == constants.EVENT_TYPE_USER_GRADE:
            notification, message_title, message_body = formatter.format_user_grade(user_data,
                                                                                    event_operation)
            onesignal_result = await self._osm.signal_message(message=notification,
                                                              email_reciepient=email)

        logging.info('onesignal_result {0}'.format(onesignal_result))

        if notification and message_title and message_body:
            message_doc = await self.db_save_message(message=message_body,
                                                     from_whom=message_title,
                                                     message_type='powiadomienie',
                                                     notification_text=notification,
                                                     notification_result=onesignal_result)

            logging.info('saved message_doc: {0}'.format(message_doc))

        else:
            return EventError('Błędnie przeprocesowane wysłanie wiadomosci OneSignal '
                              'notification: {0} message_title: {1} message_body: {2}'.format(
                notification, message_title, message_body
            ))

    async def _user_event(self, node_id, usos_id, event_type, event_operation):

        logging.info('_user_event: {0} {1} {2} {3}'.format(node_id, usos_id, event_type, event_operation))

        if event_type == constants.EVENT_TYPE_USER_POINT:

            try:
                user_point = await self.usosCall(path='services/crstests/user_point',
                                                 arguments={'node_id': node_id})

            except Exception as ex:
                logging.exception(ex)
                raise EventError('No notification for type: {0} {1}'.format(constants.EVENT_TYPE_USER_POINT, usos_id))

            logging.info('{0} user_point: {1}'.format(constants.EVENT_TYPE_USER_POINT, user_point))

            root_id_doc = await self.usosCall(path='services/crstests/root_node',
                                              arguments={'node_id': node_id, 'fields': 'root_id'})

            course_edition_doc = await self.usosCall(path='services/crstests/root_node',
                                                     arguments={'node_id': root_id_doc['root_id'],
                                                                'fields': 'course_edition'})

            logging.debug('{0} course_edition_doc: {1}'.format(constants.EVENT_TYPE_USER_POINT, course_edition_doc))

            user_point[fields.COURSE_NAME] = course_edition_doc[fields.COURSE_EDITION][fields.COURSE_NAME]
            user_point[constants.GRADER] = await self._grader(user_point['grader_id'])

            await self._one_signal(constants.EVENT_TYPE_USER_POINT, user_point, event_operation,
                                   self._context.user_doc[fields.USER_EMAIL])

        elif event_type == constants.EVENT_TYPE_USER_GRADE:

            try:
                user_grade = await self.usosCall(path='services/crstests/user_grade', arguments={'node_id': node_id})
            except Exception as ex:
                logging.exception(ex)
                raise EventError('No notification for type: {0} {1}'.format(constants.EVENT_TYPE_USER_GRADE, usos_id))

            logging.info('{0} user_grade: {1}'.format(constants.EVENT_TYPE_USER_GRADE, user_grade))

            root_id_doc = await self.usosCall(path='services/crstests/root_node',
                                              arguments={'node_id': node_id, 'fields': 'root_id'})

            course_edition_doc = await self.usosCall(path='services/crstests/root_node',
                                                     arguments={'node_id': root_id_doc['root_id'],
                                                                'fields': 'course_edition'})

            logging.debug('{0} course_edition_doc: {1}'.format(constants.EVENT_TYPE_USER_GRADE, course_edition_doc))

            user_grade[fields.COURSE_NAME] = course_edition_doc[fields.COURSE_EDITION][fields.COURSE_NAME]

            user_grade[constants.GRADER] = await self._grader(user_grade['grader_id'])

            await self._one_signal(constants.EVENT_TYPE_USER_GRADE, user_grade, event_operation,
                                   self._context.user_doc[fields.USER_EMAIL])

        raise EventError('nierozpoznany typ powiadomienia: {0}'.format(event_type))

    async def process_event(self, event_id):

        try:
            event_doc = await self.db[collections.EVENTS_USOS].find_one({fields.MONGO_ID: event_id})
            logging.info('processing event_doc: {0}'.format(event_doc))

            for entry in event_doc['entry']:
                # for user_id in entry['related_user_ids']:
                #    if user_id == self._context.user_doc[fields.USOS_USER_ID]:
                await self._user_event(
                    entry['node_id'],
                    event_doc[fields.USOS_ID],
                    event_doc['event_type'],
                    entry['operation'])

                await self._updateStatus(event_id, 'one signal send.')
                #    else:
                #        logging.info('not processing events for someone else: {0}'.format(event_doc))
        except Exception as ex:
            await self._updateStatus(event_id, 'processing failed')
            logging.exception(ex)
