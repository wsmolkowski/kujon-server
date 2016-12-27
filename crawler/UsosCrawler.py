# coding=UTF-8

import logging
from datetime import datetime
from datetime import timedelta, date

from bson.objectid import ObjectId
from tornado import gen
from tornado.util import ObjectDict

from commons import utils
from commons.AESCipher import AESCipher
from commons.UsosCaller import UsosCaller, AsyncCaller
from commons.constants import fields, collections
from commons.enumerators import ExceptionTypes
from commons.mixins.ApiMixin import ApiMixin
from commons.mixins.ApiTermMixin import ApiTermMixin
from commons.mixins.ApiUserMixin import ApiUserMixin
from commons.mixins.CrsTestsMixin import CrsTestsMixin
from commons.mixins.OneSignalMixin import OneSignalMixin


class UsosCrawler(ApiMixin, ApiUserMixin, CrsTestsMixin, OneSignalMixin, ApiTermMixin):
    EXCEPTION_TYPE = ExceptionTypes.CRAWLER.value

    def __init__(self, config):
        self.config = config
        self._aes = AESCipher(self.config.AES_SECRET)

    @property
    def aes(self):
        return self._aes

    def do_refresh(self):
        return self._context.refresh

    async def _setUp(self, user_id, setup_usos=True, refresh=False):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        self._context = ObjectDict()
        self._context.refresh = refresh
        self._context.prepare_curl_callback = self.config.PREPARE_CURL_CALLBACK
        self._context.proxy_url = self.config.PROXY_HOST
        self._context.proxy_port = self.config.PROXY_PORT
        self._context.remote_ip = None
        self._context.http_client = utils.http_client()
        self._context.user_doc = await self.db_get_user(user_id)

        if not self._context.user_doc:
            self._context.user_doc = await self.db_get_archive_user(user_id)

        if setup_usos:
            self._context.usos_doc = await self.db_get_usos(self._context.user_doc[fields.USOS_ID])
            self._context.base_uri = self._context.usos_doc[fields.USOS_URL]
            self._context.consumer_token = dict(key=self._context.usos_doc[fields.CONSUMER_KEY],
                                                secret=self._context.usos_doc[fields.CONSUMER_SECRET])

            self._context.access_token = dict(key=self._context.user_doc[fields.ACCESS_TOKEN_KEY],
                                              secret=self._context.user_doc[fields.ACCESS_TOKEN_SECRET])

    def get_current_user(self):
        return self._context.user_doc

    def get_current_usos(self):
        return self._context.usos_doc

    def getUserId(self, return_object_id=True):
        if self.get_current_user():
            if return_object_id:
                return self.get_current_user()[fields.MONGO_ID]
            return str(self.get_current_user()[fields.MONGO_ID])
        return

    def getEncryptedUserId(self):
        return self.aes.encrypt(self.getUserId(return_object_id=False)).decode()

    def getUsosId(self):
        if self.get_current_usos():
            return self.get_current_user()[fields.USOS_ID]
        return

    def get_auth_http_client(self):
        return self._context.http_client

    async def __process_courses_editions(self):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            logging.error('Empty response from: api_courses_editions() Not processing.')
            return

        # users_ids = list()
        courses_terms = list()
        # course_units_ids = list()

        for term, courses in list(courses_editions[fields.COURSE_EDITIONS].items()):
            for course in courses:

                try:
                    courses_terms.append(self.api_course_term(course[fields.COURSE_ID],
                                                              course[fields.TERM_ID],
                                                              extra_fetch=False))
                except Exception as ex:
                    logging.exception(ex)
                    continue

                    # for lecturer in course[fields.LECTURERS]:
                    #     if fields.USER_ID in lecturer and lecturer[fields.USER_ID] not in users_ids:
                    #         users_ids.append(lecturer[fields.USER_ID])
                    #     if fields.ID in lecturer and lecturer[fields.ID] not in users_ids:
                    #         users_ids.append(lecturer[fields.ID])
                    # for participant in course[fields.PARTICIPANTS]:
                    #     if fields.USER_ID in participant and participant[fields.USER_ID] not in users_ids:
                    #         users_ids.append(participant[fields.USER_ID])
                    #     if fields.ID in participant and participant[fields.ID] not in users_ids:
                    #         users_ids.append(participant[fields.ID])
                    # for coordinator in course[fields.COORDINATORS]:
                    #     if fields.USER_ID in coordinator and coordinator[fields.USER_ID] not in users_ids:
                    #         users_ids.append(coordinator[fields.USER_ID])
                    #     if fields.ID in coordinator and coordinator[fields.ID] not in users_ids:
                    #         users_ids.append(coordinator[fields.ID])
                    #
                    # for course_unit in course['course_units_ids']:
                    #     if course_unit not in course_units_ids:
                    #         course_units_ids.append(course_unit)

        try:
            await gen.multi(courses_terms)
        except Exception as ex:
            await self.exc(ex, finish=False)

            # api_user_infos = list()
            # for user_id in users_ids:
            #     api_user_infos.append(self.api_user_info(user_id))
            #
            # try:
            #     await api_user_infos
            # except Exception as ex:
            #     await self.exc(ex, finish=False)
            #
            # units_groups = list()
            # for unit in course_units_ids:
            #     units_groups.append(self.api_unit(unit))
            #     units_groups.append(self.api_group(unit))
            #
            # try:
            #     await units_groups
            # except Exception as ex:
            #     await self.exc(ex, finish=False)

    async def __process_crstests(self):
        crstests_doc = await self.api_crstests()

        grade_points = []
        for crstest in crstests_doc['tests']:
            grade_points.append(self.api_crstests_grades(crstest['node_id']))
            grade_points.append(self.api_crstests_points(crstest['node_id']))

        await gen.multi(grade_points)

    @staticmethod
    def __get_next_monday(monday):
        return monday + timedelta(days=7)

    @staticmethod
    def __get_monday():
        today = date.today()
        return today - timedelta(days=(today.weekday()) % 7)

    async def initial_user_crawl(self, user_id, refresh=False):
        try:
            await self._setUp(user_id)

            if refresh:
                skip_collections = [collections.USERS, collections.JOBS_QUEUE,
                                    collections.JOBS_LOG, collections.MESSAGES,
                                    collections.SEARCH, collections.TOKENS,
                                    collections.EMAIL_QUEUE, collections.EMAIL_QUEUE_LOG,
                                    collections.EXCEPTIONS, collections.SUBSCRIPTIONS,
                                    collections.REMOTE_IP_HISTORY]

                await self.remove_user_data(skip_collections)

            user_doc = await self.api_user_usos_info()

            await self._setUp(user_id)

            await self.api_thesis(user_info=user_doc)
            await self.__process_courses_editions()
            await self.api_terms()
            await self.api_programmes(user_info=user_doc)
            await self.api_faculties(user_info=user_doc)
            await self.__process_crstests()

        except Exception as ex:
            await self.exc(ex, finish=False)

    async def unsubscribe(self, user_id=None):
        if user_id:
            await self._setUp(user_id)

        try:
            await UsosCaller(self._context).call(path='services/events/unsubscribe')
            self.db_remove(collections.SUBSCRIPTIONS, {fields.USER_ID: self.getUserId()})
        except Exception as ex:
            logging.warning(ex)

    async def subscribe(self, user_id):

        await self._setUp(user_id)

        await self.unsubscribe()

        callback_url = '{0}/{1}'.format(self.config.DEPLOY_EVENT, self.getUsosId())

        for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
            try:
                subscribe_doc = await UsosCaller(self._context).call(path='services/events/subscribe_event',
                                                                     arguments={
                                                                         'event_type': event_type,
                                                                         'callback_url': callback_url,
                                                                         'verify_token': self.getEncryptedUserId()
                                                                     })
                subscribe_doc['event_type'] = event_type
                subscribe_doc[fields.USER_ID] = self.getUserId()

                await self.db_insert(collections.SUBSCRIPTIONS, subscribe_doc)
            except Exception as ex:
                await self.exc(ex, finish=False)

    async def archive_user(self, user_id):
        await self._setUp(user_id, setup_usos=False)

        await self.unsubscribe()

        await self.remove_user_data([collections.USERS_ARCHIVE, ])

    async def remove_user_data(self, skip_collections=None):
        if not skip_collections:
            skip_collections = list()

        try:
            collections = await self.db.collection_names(include_system_collections=False)
            remove_tasks = list()
            for collection in collections:

                if collection in skip_collections:
                    continue

                exists = await self.db[collection].find_one({fields.USER_ID: {'$exists': True, '$ne': False}})
                if exists:
                    remove_tasks.append(self.db[collection].remove({fields.USER_ID: self.getUserId()}))

            result = await gen.multi(remove_tasks)
            logging.info('removed user data for user_id: {0} resulted in: {1}'.format(self.getUserId(), result))
        except Exception as ex:
            logging.exception(ex)

    async def __user_event(self, user_id, node_id, usos_id):
        try:
            user_doc = await self.db_find_user_by_usos_id(user_id, usos_id)

            await self._setUp(user_doc[fields.MONGO_ID])

            caller = UsosCaller(self._context)

            user_point = await caller.call(path='services/crstests/user_point',
                                           arguments={'node_id': node_id})

            logging.debug('user_point: {0}'.format(user_point))

            if user_point:
                signal_point = await self.signal_message('wiadomosc {0}'.format(user_point),
                                                         user_doc[fields.USER_EMAIL])
                logging.debug('user_point signal_response: {1}'.format(signal_point))

            user_grade = await caller.call(path='services/crstests/user_grade',
                                           arguments={'node_id': node_id})
            logging.debug('user_grade: {0}'.format(user_grade))

            if user_grade:
                message_text = 'wiadomosc {0}'.format(user_grade)
                signal_grade = await self.signal_message(message_text, user_doc[fields.USER_EMAIL])
                await self.db_save_message(message_text, from_whom='Komunikat z USOS', message_type='powiadomienie')

                logging.debug('user_point signal_response: {1}'.format(signal_grade))

        except Exception as ex:
            logging.error(
                'Exception while user event processing for user_id: {0} and node_id: {1}'.format(user_id, node_id))
            await self.exc(ex, finish=False)

    async def process_event(self, event):
        logging.info('processing event: {0}'.format(event))

        user_events = list()
        for entry in event['entry']:
            for user_id in entry['related_user_ids']:
                user_events.append(self.__user_event(user_id, entry['node_id'], event[fields.USOS_ID]))

        result = await gen.multi(user_events)
        logging.debug('process_event results: {0}'.format(result))

    async def notifier_status(self):
        # unused
        try:
            timestamp = datetime.now()

            usoses = await self.db_usoses()
            for usos_doc in usoses:
                try:
                    data = await AsyncCaller().call_async(path='services/events/notifier_status',
                                                          base_url=usos_doc[fields.USOS_URL])

                    data[fields.CREATED_TIME] = timestamp
                    data[fields.USOS_ID] = usos_doc[fields.USOS_ID]

                    await self.db_insert(collections.NOTIFIER_STATUS, data)
                except Exception as ex:
                    await self.exc(ex, finish=False)

        except Exception as ex:
            self.exc(ex, finish=False)
