# coding=UTF-8

import logging

from bson.objectid import ObjectId

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
        await super(EventAbstractHandler, self).prepare()

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

    async def _buildContext(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        user_doc = await self.db_get_user(user_id)
        if not user_doc:
            raise EventError('Nierozpoznany parametr użytkownika.')

        usos_doc = await self.db_get_usos(user_doc[fields.USOS_ID])
        self._context = Context(self.config, user_doc=user_doc, usos_doc=usos_doc)
        self._context.settings = await self.db_settings(self.getUserId())

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

        if notification and message_title and message_body:
            await self.db_save_message(message=message_body,
                                       from_whom=message_title,
                                       message_type='powiadomienie',
                                       notification_text=notification,
                                       notification_result=onesignal_result)
        else:
            return EventError('Błędnie przeprocesowane wysłanie wiadomosci OneSignal')

    async def _user_event(self, node_id, usos_id, event_type, event_operation):
        logging.debug('_user_event: {0} {1} {2} {3}'.format(node_id, usos_id, event_type, event_operation))
        try:

            if event_type == constants.EVENT_TYPE_USER_POINT:

                user_point = await self.usosCall(path='services/crstests/user_point',
                                                 arguments={'node_id': node_id})
                logging.debug('{0} user_point: {1}'.format(constants.EVENT_TYPE_USER_POINT, user_point))

                if not user_point:
                    raise EventError(
                        'No notification for type: {0} {1}'.format(constants.EVENT_TYPE_USER_POINT, usos_id))

                # get info about course_edition
                root_id_doc = await self.usosCall(path='services/crstests/root_node',
                                                  arguments={'node_id': node_id, 'fields': 'root_id'})

                course_edition_doc = await self.usosCall(path='services/crstests/root_node',
                                                         arguments={'node_id': root_id_doc['root_id'],
                                                                    'fields': 'course_edition'})

                user_point[fields.COURSE_NAME] = course_edition_doc[fields.COURSE_EDITION][fields.COURSE_NAME]
                user_point[constants.GRADER] = await self._grader(user_point['grader_id'])

                await self._one_signal(constants.EVENT_TYPE_USER_POINT, user_point, event_operation,
                                       self._context.user_doc[fields.USER_EMAIL])

            elif event_type == constants.EVENT_TYPE_USER_GRADE:

                user_grade = await self.usosCall(path='services/crstests/user_grade', arguments={'node_id': node_id})
                logging.debug('{0} user_grade: {1}'.format(constants.EVENT_TYPE_USER_GRADE, user_grade))

                if not user_grade:
                    raise EventError(
                        'No notification for type: {0} {1}'.format(constants.EVENT_TYPE_USER_GRADE, usos_id))

                # get info about course_edition
                root_id_doc = await self.usosCall(path='services/crstests/root_node',
                                                  arguments={'node_id': node_id, 'fields': 'root_id'})

                course_edition_doc = await self.usosCall(path='services/crstests/root_node',
                                                         arguments={'node_id': root_id_doc['root_id'],
                                                                    'fields': 'course_edition'})

                user_grade[fields.COURSE_NAME] = course_edition_doc[fields.COURSE_EDITION][fields.COURSE_NAME]

                user_grade[constants.GRADER] = await self._grader(user_grade['grader_id'])

                await self._one_signal(constants.EVENT_TYPE_USER_GRADE, user_grade, event_operation,
                                       self._context.user_doc[fields.USER_EMAIL])

            raise EventError('nierozpoznany typ powiadomienia: {0}'.format(event_type))

        except Exception as ex:
            await self.exc(ex, finish=False)

    async def process_event(self, event):
        for entry in event['entry']:
            for user_id in entry['related_user_ids']:
                if user_id == self._context.user_doc[fields.USOS_USER_ID]:
                    await self._user_event(user_id,
                                           entry['node_id'],
                                           event[fields.USOS_ID],
                                           event['event_type'],
                                           entry['operation'])
                else:
                    logging.debug('not processing events for someone else: {0}'.format(event))
