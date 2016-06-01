# coding=UTF-8

import logging
import traceback
from datetime import datetime
from datetime import timedelta, date

from bson.objectid import ObjectId
from tornado import gen

from commons import constants, utils
from commons.AESCipher import AESCipher
from commons.errors import CrawlerException, UsosClientError
from commons.mixins.ApiMixin import ApiMixin


class UsosCrawler(ApiMixin):
    EXCEPTION_TYPE = 'usoscrawler'
    EVENT_TYPES = ['crstests/user_grade', 'grades/grade', 'crstests/user_point']

    def __init__(self):
        self.aes = AESCipher()

    _user_doc = None

    @property
    def user_doc(self):
        return self._user_doc

    _usos_doc = None

    @property
    def usos_doc(self):
        return self._usos_doc

    @property
    def usos_id(self):
        return self.user_doc[constants.USOS_ID]

    @property
    def user_id(self):
        return self.user_doc[constants.MONGO_ID]

    @gen.coroutine
    def get_usos(self, key, value):
        raise gen.Return(self._usos_doc)

    @gen.coroutine
    def _exc(self, exception):
        try:
            exc_doc = {
                'args': exception.args,
                'message': str(exception),
                constants.TRACEBACK: traceback.format_exc(),
                constants.EXCEPTION_TYPE: self.EXCEPTION_TYPE,
                constants.CREATED_TIME: datetime.now()
            }

            if hasattr(self, 'user_doc') and self.user_doc:
                exc_doc[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
                exc_doc[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
                exc_doc[constants.EXCEPTION_TYPE] = self.EXCEPTION_TYPE

            yield self.db_insert(constants.COLLECTION_EXCEPTIONS, utils.serialize(exc_doc))
            logging.error(exc_doc)
        except Exception, ex:
            logging.exception(ex)

        raise gen.Return(None)


    @gen.coroutine
    def __subscribe(self):

        for event_type in self.EVENT_TYPES:
            try:
                subscribe_doc = yield self.usos_subscribe(event_type, self.user_doc[constants.MONGO_ID])
                yield self.db_insert(constants.COLLECTION_SUBSCRIPTION, subscribe_doc)
            except Exception, ex:
                yield self._exc(ex)

    @gen.coroutine
    def __build_courses(self):

        courses = list()
        existing_courses = list()
        # get courses that exists in mongo and remove from list to fetch
        existing_courses_extended = yield self.db_courses(self.usos_id)
        for course_extended in existing_courses_extended:
            existing_courses.append(course_extended[constants.COURSE_ID])

        # get courses from course_edition
        courses_editions = yield self.db_courses_editions(self.user_id)
        for course_edition in courses_editions:
            if course_edition[constants.COURSE_ID] not in existing_courses:
                existing_courses.append(course_edition[constants.COURSE_ID])
                courses.append(course_edition[constants.COURSE_ID])

        # get courses
        for course_id in courses:
            try:
                result = yield self.usos_course(course_id)
                if result:
                    # change faculty_id to faculty name
                    faculty_doc = yield self.db_faculty(result[constants.FACULTY_ID], self.usos_id)
                    if not faculty_doc:
                        faculty_doc = yield self.usos_faculty(result[constants.FACULTY_ID])
                        yield self.db_insert(constants.COLLECTION_FACULTIES, faculty_doc)

                    result[constants.FACULTY_NAME] = faculty_doc[constants.FACULTY_NAME]
                    yield self.db_insert(constants.COLLECTION_COURSES, result)
                else:
                    logging.warning("no course for course_id: %r.", course_id)
            except Exception, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __api_unit(self, unit_id):
        unit_doc = yield self.db_unit(unit_id, self.usos_id)
        if not unit_doc:
            try:
                result = yield self.usos_unit(unit_id)
                if result:
                    yield self.db_insert(constants.COLLECTION_COURSES_UNITS, result)
                else:
                    logging.warning("no unit for unit_id: {0} and usos_id: {1)".format(unit_id, self.usos_id))
            except UsosClientError, ex:
                yield self.exc(ex, finish=False)

        raise gen.Return(None)

    @gen.coroutine
    def __api_group(self, group_id):
        group_doc = yield self.db_group(group_id, self.usos_id)
        if not group_doc:
            try:
                result = yield self.usos_group(group_id)
                if result:
                    yield self.db_insert(constants.COLLECTION_GROUPS, result)
                else:
                    msg = "no group for group_id: {} and usos_id: {}.".format(group_id, self.usos_id)
                    logging.info(msg)
            except UsosClientError, ex:
                yield self.exc(ex, finish=False)

        raise gen.Return(None)

    @gen.coroutine
    def __process_courses_editions(self):
        courses_editions = yield self.api_courses_editions()

        users_ids = list()
        courses_terms = list()
        course_units_ids = list()

        for term, courses in courses_editions[constants.COURSE_EDITIONS].items():
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

        api_units = list()
        api_groups = list()
        for unit in course_units_ids:
            api_units.append(self.__api_unit(unit))
            api_groups.append(self.__api_group(unit))

        yield api_units
        yield api_groups

        raise gen.Return(None)

    @gen.coroutine
    def initial_user_crawl(self, user_id):
        try:
            self._user_doc = yield self.db_get_user(user_id)
            if not self.user_doc:
                raise CrawlerException("Initial crawler not started. Unknown user with id: %r.", user_id)

            self._usos_doc = yield self.db_get_usos(self.user_doc[constants.USOS_ID])

            yield self.api_user_info()
            yield self.api_courses_editions()
            yield self.api_tt(self.__get_monday())
            yield self.api_programmes()
            yield self.__process_courses_editions()
            # yield self.__build_courses()

            yield self.__subscribe()
        except Exception, ex:
            yield self._exc(ex)

    @gen.coroutine
    def daily_crawl(self):
        users = yield self.db_users()
        for user_doc in users:
            try:
                logging.debug('updating daily crawl for user: {0}'.format(user_doc[constants.MONGO_ID]))

                self._user_doc = yield self.db_get_user(user_doc[constants.MONGO_ID])
                if not self.user_doc:
                    raise CrawlerException("Daily crawler not started. Unknown user with id: %r.",
                                           user_doc[constants.MONGO_ID])

                self._usos_doc = yield self.db_get_usos(self.user_doc[constants.USOS_ID])

                yield self.__process_courses_editions()
            except Exception, ex:
                yield self._exc(ex)

    @staticmethod
    def __get_next_monday(monday):
        return monday + timedelta(days=7)

    @staticmethod
    def __get_monday():
        today = date.today()
        monday = today - timedelta(days=(today.weekday()) % 7)
        return monday

    @gen.coroutine
    def update_user_crawl(self, user_id):
        try:
            self._user_doc = yield self.db_get_user(user_id)
            if not self.user_doc:
                raise CrawlerException("Initial crawler not started. Unknown user with id: %r.", user_id)

            self._usos_doc = yield self.db_get_usos(self.user_doc[constants.USOS_ID])

            courses_conducted = yield self.db_courses_conducted(user_id)

            # yield self.__build_course_editions_conducted(courses_conducted)
        except Exception, ex:
            yield self._exc(ex)

    @gen.coroutine
    def update_time_tables(self):
        monday = self.__get_monday()
        next_monday = self.__get_next_monday(monday)

        users = yield self.db_users()
        for user_doc in users:
            try:
                logging.debug(
                    'updating time table for user: {0} and monday: {1}'.format(user_doc[constants.MONGO_ID], monday))
                self.api_tt(monday)
                self.api_tt(next_monday)

                logging.debug('updating time table for user: {0}'.format(user_doc[constants.MONGO_ID]))
            except Exception, ex:
                yield self._exc(ex)

    @gen.coroutine
    def unsubscribe(self, user_id):
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            user_doc_archive = yield self.db_archive_user(user_id)

            if not user_doc_archive:
                raise CrawlerException(
                    "Unsubscribe process not started. Unknown user with id: %r or user not paired with any USOS",
                    user_id)

            usos_doc = yield self.db_get_usos(user_doc_archive[constants.USOS_ID])

            if constants.USOS_ID in user_doc_archive:
                try:
                    yield self.usos_unsubscribe(usos_doc, user_doc_archive)
                except Exception, ex:
                    yield self._exc(ex)
        except Exception, ex:
            yield self._exc(ex)

    @gen.coroutine
    def notifier_status(self):
        try:
            timestamp = datetime.now()

            usoses = yield self.db_usoses()
            for usos_doc in usoses:
                try:
                    data = yield self.notifier_status(usos_doc)
                    data[constants.CREATED_TIME] = timestamp
                    data[constants.USOS_ID] = usos_doc[constants.USOS_ID]

                    yield self.db_insert(constants.COLLECTION_NOTIFIER_STATUS, data)
                except Exception, ex:
                    yield self._exc(ex)

        except Exception, ex:
            self._exc(ex)

# @gen.coroutine
# def main():
#     crawler = UsosCrawler()
#     user_id = '574eb275d54c4b8a3c02ac55'
#     yield crawler.initial_user_crawl(user_id)
#     # yield crawler.daily_crawl()
#     # yield crawler.update_user_crawl(user_id)
#     # yield crawler.update_time_tables()
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
