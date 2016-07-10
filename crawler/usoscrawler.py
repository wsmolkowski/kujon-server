# coding=UTF-8

import logging
from datetime import datetime
from datetime import timedelta, date

from bson.objectid import ObjectId
from tornado import gen

from commons import constants
from commons.AESCipher import AESCipher
from commons.errors import CrawlerException
from commons.mixins.ApiMixin import ApiMixin


class UsosCrawler(ApiMixin):
    EXCEPTION_TYPE = 'usoscrawler'

    def __init__(self):
        self.aes = AESCipher()

    _usos_doc = None

    @property
    def usos_doc(self):
        return self._usos_doc

    @property
    def usos_id(self):
        return self.get_current_user()[constants.USOS_ID]

    @property
    def user_id(self):
        return self.get_current_user()[constants.MONGO_ID]

    _user_doc = None

    def get_current_user(self):
        return self._user_doc

    def get_current_usos(self):
        return self._usos_doc

    @gen.coroutine
    def __process_courses_editions(self):
        courses_editions = yield self.api_courses_editions()

        users_ids = list()
        courses_terms = list()
        course_units_ids = list()

        for term, courses in list(courses_editions[constants.COURSE_EDITIONS].items()):
            for course in courses:

                courses_terms.append(self.api_course_term(course[constants.COURSE_ID],
                                                          course[constants.TERM_ID],
                                                          extra_fetch=False))

                for lecturer in course[constants.LECTURERS]:
                    if constants.USER_ID in lecturer and lecturer[constants.USER_ID] not in users_ids:
                        users_ids.append(lecturer[constants.USER_ID])
                    if constants.ID in lecturer and lecturer[constants.ID] not in users_ids:
                        users_ids.append(lecturer[constants.ID])
                for participant in course[constants.PARTICIPANTS]:
                    if constants.USER_ID in participant and participant[constants.USER_ID] not in users_ids:
                        users_ids.append(participant[constants.USER_ID])
                    if constants.ID in participant and participant[constants.ID] not in users_ids:
                        users_ids.append(participant[constants.ID])
                for coordinator in course[constants.COORDINATORS]:
                    if constants.USER_ID in coordinator and coordinator[constants.USER_ID] not in users_ids:
                        users_ids.append(coordinator[constants.USER_ID])
                    if constants.ID in coordinator and coordinator[constants.ID] not in users_ids:
                        users_ids.append(coordinator[constants.ID])

                for course_unit in course['course_units_ids']:
                    if course_unit not in course_units_ids:
                        course_units_ids.append(course_unit)

        yield courses_terms

        api_user_infos = list()
        for user_id in users_ids:
            api_user_infos.append(self.api_user_info(user_id))

        yield api_user_infos

        units_groups = list()
        for unit in course_units_ids:
            units_groups.append(self.api_unit(unit))
            units_groups.append(self.api_group(unit))

        yield units_groups

        raise gen.Return()

    @staticmethod
    def __get_next_monday(monday):
        return monday + timedelta(days=7)

    @staticmethod
    def __get_monday():
        today = date.today()
        monday = today - timedelta(days=(today.weekday()) % 7)
        return monday

    @gen.coroutine
    def _setUp(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        self._user_doc = yield self.db_get_user(user_id)
        if not self._user_doc:
            self._user_doc = yield self.db_get_archive_user(user_id)

        if not self._user_doc:
            raise CrawlerException(
                "Process not started. Unknown user with id: %r or user not paired with any USOS", user_id)

        self._usos_doc = yield self.db_get_usos(self._user_doc[constants.USOS_ID])

    @gen.coroutine
    def initial_user_crawl(self, user_id):
        try:
            yield self._setUp(user_id)

            yield self.api_user_info()
            yield self.api_courses_editions()
            yield self.__process_courses_editions()
            yield self.api_terms()
            yield self.api_programmes()
            yield self.api_faculties()
            yield self.api_tt(self.__get_monday())
        except Exception as ex:
            yield self.exc(ex, finish=False)

    @gen.coroutine
    def subscribe(self, user_id):

        yield self._setUp(user_id)

        for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
            try:
                subscribe_doc = yield self.usos_subscribe(event_type, self.get_current_user()[constants.MONGO_ID])
                yield self.db_insert(constants.COLLECTION_SUBSCRIPTIONS, subscribe_doc)
            except Exception as ex:
                logging.exception(ex)
                yield self.exc(ex, finish=False)

    @gen.coroutine
    def unsubscribe(self, user_id):
        try:
            yield self._setUp(user_id)

            yield self.usos_unsubscribe()

        except Exception as ex:
            yield self.exc(ex, finish=False)

    @gen.coroutine
    def notifier_status(self):
        # unused
        try:
            timestamp = datetime.now()

            usoses = yield self.db_usoses()
            for usos_doc in usoses:
                try:
                    data = yield self.notifier_status(usos_doc)
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
#     user_id = '577cdff7d54c4b87b0494ef3'
#     yield crawler.initial_user_crawl(user_id)
#     # yield crawler.unsubscribe(user_id)
#
#
# if __name__ == '__main__':
#     import logging
#     from tornado import ioloop
#     from tornado.options import parse_command_line
#
#     parse_command_line()
#     logging.getLogger().setLevel(logging.DEBUG)
#     io_loop = ioloop.IOLoop.current()
#     io_loop.run_sync(main)
