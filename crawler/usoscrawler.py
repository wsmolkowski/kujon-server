# coding=UTF-8

import logging
from datetime import datetime
from datetime import timedelta, date

from bson.objectid import ObjectId
from tornado import gen
from tornado.util import ObjectDict

from commons import constants, utils, settings
from commons.AESCipher import AESCipher
from commons.UsosCaller import UsosCaller
from commons.mixins.ApiMixin import ApiMixin
from commons.mixins.ApiUserMixin import ApiUserMixin
from commons.mixins.CrsTestsMixin import CrsTestsMixin
from commons.mixins.OneSignalMixin import OneSignalMixin


class UsosCrawler(ApiMixin, ApiUserMixin, CrsTestsMixin, OneSignalMixin):
    EXCEPTION_TYPE = 'usoscrawler'

    def __init__(self):
        self.aes = AESCipher()

    @gen.coroutine
    def _setUp(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        self._context = ObjectDict()
        self._context.http_client = utils.http_client()
        self._context.user_doc = yield self.db_get_user(user_id)
        if not self._context.user_doc:
            self._context.user_doc = yield self.db_get_archive_user(user_id)

        self._context.usos_doc = yield self.db_get_usos(self._context.user_doc[constants.USOS_ID])
        self._context.base_uri = self._context.usos_doc[constants.USOS_URL]
        self._context.consumer_token = dict(key=self._context.usos_doc[constants.CONSUMER_KEY],
                                            secret=self._context.usos_doc[constants.CONSUMER_SECRET])

        self._context.access_token = dict(key=self._context.user_doc[constants.ACCESS_TOKEN_KEY],
                                          secret=self._context.user_doc[constants.ACCESS_TOKEN_SECRET])

    def get_current_user(self):
        return self._context.user_doc

    def get_current_usos(self):
        return self._context.usos_doc

    def getUserId(self):
        if self.get_current_user():
            return ObjectId(self.get_current_user()[constants.MONGO_ID])
        return None

    def getUsosId(self):
        if self.get_current_usos():
            return self.get_current_user()[constants.USOS_ID]
        return None

    def get_auth_http_client(self):
        return self._context.http_client

    @gen.coroutine
    def __process_courses_editions(self):
        courses_editions = yield self.api_courses_editions()

        # users_ids = list()
        courses_terms = list()
        # course_units_ids = list()

        for term, courses in list(courses_editions[constants.COURSE_EDITIONS].items()):
            for course in courses:

                try:
                    courses_terms.append(self.api_course_term(course[constants.COURSE_ID],
                                                              course[constants.TERM_ID],
                                                              extra_fetch=False))
                except Exception as ex:
                    logging.exception(ex)
                    continue

                    # for lecturer in course[constants.LECTURERS]:
                    #     if constants.USER_ID in lecturer and lecturer[constants.USER_ID] not in users_ids:
                    #         users_ids.append(lecturer[constants.USER_ID])
                    #     if constants.ID in lecturer and lecturer[constants.ID] not in users_ids:
                    #         users_ids.append(lecturer[constants.ID])
                    # for participant in course[constants.PARTICIPANTS]:
                    #     if constants.USER_ID in participant and participant[constants.USER_ID] not in users_ids:
                    #         users_ids.append(participant[constants.USER_ID])
                    #     if constants.ID in participant and participant[constants.ID] not in users_ids:
                    #         users_ids.append(participant[constants.ID])
                    # for coordinator in course[constants.COORDINATORS]:
                    #     if constants.USER_ID in coordinator and coordinator[constants.USER_ID] not in users_ids:
                    #         users_ids.append(coordinator[constants.USER_ID])
                    #     if constants.ID in coordinator and coordinator[constants.ID] not in users_ids:
                    #         users_ids.append(coordinator[constants.ID])
                    #
                    # for course_unit in course['course_units_ids']:
                    #     if course_unit not in course_units_ids:
                    #         course_units_ids.append(course_unit)

        try:
            yield courses_terms
        except Exception as ex:
            yield self.exc(ex, finish=False)

        # api_user_infos = list()
        # for user_id in users_ids:
        #     api_user_infos.append(self.api_user_info(user_id))
        #
        # try:
        #     yield api_user_infos
        # except Exception as ex:
        #     yield self.exc(ex, finish=False)
        #
        # units_groups = list()
        # for unit in course_units_ids:
        #     units_groups.append(self.api_unit(unit))
        #     units_groups.append(self.api_group(unit))
        #
        # try:
        #     yield units_groups
        # except Exception as ex:
        #     yield self.exc(ex, finish=False)

        raise gen.Return()

    @gen.coroutine
    def __process_crstests(self):
        crstests_doc = yield self.api_crstests()

        grade_points = []
        for crstest in crstests_doc['tests']:
            grade_points.append(self.api_crstests_grades(crstest['node_id']))
            grade_points.append(self.api_crstests_points(crstest['node_id']))

        yield grade_points

    @staticmethod
    def __get_next_monday(monday):
        return monday + timedelta(days=7)

    @staticmethod
    def __get_monday():
        today = date.today()
        monday = today - timedelta(days=(today.weekday()) % 7)
        return monday

    @gen.coroutine
    def initial_user_crawl(self, user_id):
        try:
            yield self._setUp(user_id)

            yield self.api_user_info()
            yield self.api_thesis()
            yield self.api_courses_editions()
            yield self.__process_courses_editions()
            yield self.api_terms()
            yield self.api_programmes()
            yield self.api_faculties()
            yield self.api_tt(self.__get_monday())
            yield self.__process_crstests()

        except Exception as ex:
            yield self.exc(ex, finish=False)

    @gen.coroutine
    def subscribe(self, user_id):

        yield self._setUp(user_id)

        callback_url = '{0}/{1}'.format(settings.DEPLOY_EVENT, self.getUsosId())

        for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
            try:
                subscribe_doc = yield UsosCaller(self._context).call(path='services/events/subscribe_event',
                                                                     arguments={
                                                                         'event_type': event_type,
                                                                         'callback_url': callback_url,
                                                                         'verify_token': self.get_current_user()[
                                                                             constants.MONGO_ID]
                                                                     })
                subscribe_doc['event_type'] = event_type
                subscribe_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

                yield self.db_insert(constants.COLLECTION_SUBSCRIPTIONS, subscribe_doc)
            except Exception as ex:
                logging.exception(ex)
                yield self.exc(ex, finish=False)

    @gen.coroutine
    def archive_user(self, user_id):
        yield self._setUp(user_id)

        try:
            yield UsosCaller(self._context).call(path='services/events/unsubscribe')
        except Exception as ex:
            logging.warning(ex)

        collections = yield self.db.collection_names()

        remove_collections = []
        for collection in collections:

            if collection == constants.COLLECTION_USERS_ARCHIVE:
                continue

            exists = yield self.db[collection].find_one({constants.USER_ID: {'$exists': True, '$ne': False}})
            if exists:
                remove_collections.append(self.db[collection].remove({constants.USER_ID: user_id}))

        result = yield remove_collections

        logging.info('removed user data for user_id: {0} resulted in: {1}'.format(user_id, result))

        raise gen.Return()

    @gen.coroutine
    def __user_event(self, user_id, node_id):
        try:
            user_doc = yield self.db_find_user_id(user_id)
            usos_doc = yield self.db_get_usos(user_doc[constants.USOS_ID])

            context = ObjectDict()
            context.base_uri = usos_doc[constants.USOS_URL]
            context.consumer_token = dict(key=usos_doc[constants.CONSUMER_KEY],
                                          secret=usos_doc[constants.CONSUMER_SECRET])
            context.access_token = dict(key=user_doc[constants.ACCESS_TOKEN_KEY],
                                        secret=user_doc[constants.ACCESS_TOKEN_SECRET])

            caller = UsosCaller(context)

            user_point = yield caller.call(path='services/crstests/user_point',
                                           arguments={'node_id': node_id})

            logging.debug('user_point: {0}'.format(user_point))

            if user_point:
                signal_point = yield self.signal_message('wiadomosc {0}'.format(user_point),
                                                         user_doc[constants.USER_EMAIL])
                logging.debug('user_point signal_response: {1}'.format(signal_point))

            user_grade = yield caller.call(path='services/crstests/user_grade',
                                           arguments={'node_id': node_id})
            logging.debug('user_grade: {0}'.format(user_grade))

            if user_grade:
                signal_grade = yield self.signal_message('wiadomosc {0}'.format(user_grade),
                                                         user_doc[constants.USER_EMAIL])
                logging.debug('user_point signal_response: {1}'.format(signal_grade))

        except Exception as ex:
            logging.error(
                'Exception while user event processing for user_id: {0} and node_id: {1}'.format(user_id, node_id))
            yield self.exc(ex, finish=False)

        raise gen.Return()

    @gen.coroutine
    def process_event(self, event):
        logging.info(event)
        user_events = list()
        for entry in event['entry']:
            for user_id in entry['related_user_ids']:
                user_events.append(self.__user_event(user_id, entry['node_id']))

        result = yield user_events
        logging.debug('process_event results: {0}'.format(result))

    @gen.coroutine
    def notifier_status(self):
        # unused
        try:
            timestamp = datetime.now()

            usoses = yield self.db_usoses()
            for usos_doc in usoses:
                try:
                    data = yield UsosCaller().async(path='services/events/notifier_status',
                                                    base_url=usos_doc[constants.USOS_URL])

                    data[constants.CREATED_TIME] = timestamp
                    data[constants.USOS_ID] = usos_doc[constants.USOS_ID]

                    yield self.db_insert(constants.COLLECTION_NOTIFIER_STATUS, data)
                except Exception as ex:
                    yield self.exc(ex, finish=False)

        except Exception as ex:
            self.exc(ex, finish=False)

# @gen.coroutine
# def main():
#     crawler = UsosCrawler()
#     user_id = '578896c9d54c4b1e083f2fe9'
#     yield crawler.initial_user_crawl(user_id)
#     # yield crawler.unsubscribe(user_id)
#
#     # event = {u'entry': [
#     #     # {u'operation': u'update', u'node_id': 62109, u'related_user_ids': [u'1279833'], u'time': 1467979077},
#     #     # {u'operation': u'update', u'node_id': 58746, u'related_user_ids': [u'1279833'], u'time': 1467979077},
#     #     # {u'operation': u'update', u'node_id': 55001, u'related_user_ids': [u'1279833'], u'time': 1467979077},
#     #     {u'operation': u'update', u'node_id': 62109, u'related_user_ids': [u'1167405'], u'time': 1467979077},
#     #     {u'operation': u'update', u'node_id': 58746, u'related_user_ids': [u'1167405'], u'time': 1467979077},
#     #     {u'operation': u'update', u'node_id': 55001, u'related_user_ids': [u'1167405'], u'time': 1467979077}
#     # ],
#     #     u'event_type': u'crstests/user_point', u'usos_id': u'DEMO'}
#     # yield crawler.process_event(event)
#
#
# if __name__ == '__main__':
#     from tornado import ioloop
#     from tornado.options import parse_command_line
#
#     parse_command_line()
#     logging.getLogger().setLevel(logging.DEBUG)
#     io_loop = ioloop.IOLoop.current()
#     io_loop.run_sync(main)
