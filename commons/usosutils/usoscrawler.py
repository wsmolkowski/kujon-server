# coding=UTF-8

import logging
import traceback
from datetime import datetime
from datetime import timedelta, date

from bson.objectid import ObjectId
from tornado import gen

from commons import constants, utils
from commons.AESCipher import AESCipher
from commons.errors import UsosClientError, CrawlerException
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin
from commons.usosutils.usosasync import UsosAsync


class UsosCrawler(UsosMixin, DaoMixin):
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
    def _exc(self, exception):
        try:
            if hasattr(self, 'user') and isinstance(exception, UsosClientError):
                exc_doc = exception
                exc_doc.append(constants.USER_ID, self.user[constants.MONGO_ID])
                exc_doc.append(constants.USOS_ID, self.user[constants.USOS_ID])
                exc_doc.append(constants.EXCEPTION_TYPE, self.EXCEPTION_TYPE)
                exc_doc.append(constants.CREATED_TIME, datetime.now())

                exc_doc = exc_doc.message
            else:
                exc_doc = {
                    'args': exception.args,
                    'message': str(exception),
                    constants.TRACEBACK: traceback.format_exc(),
                    constants.EXCEPTION_TYPE: self.EXCEPTION_TYPE,
                    constants.CREATED_TIME: datetime.now()
                }

            yield self.db_insert(constants.COLLECTION_EXCEPTIONS, utils.serialize(exc_doc))
            logging.error(exc_doc)
        except Exception, ex:
            logging.exception(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __build_user_info_photo(self, user_info_id):

        photo_doc = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.ID: user_info_id})

        if not photo_doc:
            photo_doc = yield self.usos_photo(user_info_id)
            if not photo_doc:
                yield self.insert(constants.COLLECTION_PHOTOS, photo_doc)
            else:
                logging.warn('no photo for user_info_id: {0} and usos_id: {1}'.format(user_info_id, self.usos_id))

        raise gen.Return(photo_doc)

    @gen.coroutine
    def __build_user_info(self, user_info_id=None):
        user_info_doc = yield self.db_users_info_by_user_id(self.user_id, self.usos_id)
        if self.user_id and user_info_doc:
            logging.debug("not building user info - it already exists for %r", self.user_id)
            raise gen.Return(user_info_doc[constants.ID])
        try:
            if user_info_id:
                result = yield self.usos_user_info_id(user_info_id, self.usos_id)
            else:
                result = yield self.usos_user_info(self.user_id, self.usos_id)

            yield self.db_insert(constants.COLLECTION_USERS_INFO, result)

            # if user has photo - download
            if 'has_photo' in result and result['has_photo']:
                result['has_photo'] = yield self.__build_user_info_photo(result[constants.ID])

        except UsosClientError, ex:
            yield self._exc(ex)

        raise gen.Return(result[constants.ID])

    @gen.coroutine
    def __build_course_editions_conducted(self, courses_conducted):

        for courseterm in courses_conducted:

            course_id, term_id = courseterm[constants.ID].split('|')

            course_doc = yield self.db_course_edition(self.user_id, course_id, term_id, self.usos_id)
            if course_doc:
                continue

            try:
                result = yield self.usos_course_edition(course_id, term_id, self.user_id, self.usos_id, fetch_participants=False)
                yield self.db_insert(constants.COLLECTION_COURSE_EDITION, result)

            except UsosClientError, ex:
                yield self._exc(ex)

    @gen.coroutine
    def __subscribe(self):
        client = yield self.usos_client()
        for event_type in self.EVENT_TYPES:
            try:
                subscribe_doc = client.subscribe(event_type, self.user_id)
                subscribe_doc = self.append(subscribe_doc, self.usos_id, datetime.now(), datetime.now())
                subscribe_doc[constants.USER_ID] = self.user_id
                subscribe_doc['event_type'] = event_type
                yield self.db_insert(constants.COLLECTION_SUBSCRIPTION, subscribe_doc)
            except UsosClientError, ex:
                yield self._exc(ex)

    @gen.coroutine
    def __build_time_table(self, given_date):
        client = yield self.usos_client()

        try:
            result = client.time_table(given_date)
        except UsosClientError, ex:
            yield self._exc(ex)
            raise gen.Return(None)

        if result:
            tt = dict()
            tt[constants.USOS_ID] = self.usos_id
            tt[constants.TT_STARTDATE] = str(given_date)
            tt['tts'] = result
            tt[constants.USER_ID] = self.user_id
            yield self.db_insert(constants.COLLECTION_TT, tt)

            # if existing_tt:
            #     self.dao.remove(constants.COLLECTION_TT, existing_tt)
        else:
            logging.debug("no time tables for date: %r inserted empty", given_date)

        raise gen.Return(None)

    @gen.coroutine
    def __build_programmes(self, user_info_id):
        programmes = yield self.db_users_info_programmes(user_info_id, self.usos_id)

        for programme in programmes:
            programme_doc = yield self.db_programme(programme['programme'][constants.ID], self.usos_id)
            if programme_doc:
                continue
            try:
                result = yield self.usos_programme(programme['programme'][constants.ID])

                yield self.db_insert(constants.COLLECTION_PROGRAMMES, result)
            except UsosClientError, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __build_curses_editions(self):
        course_edition = yield self.db_courses_editions(self.user_id)

        result = yield self.usos_courses_editions(self.user_id, self.usos_id)

        if not course_edition:
            yield self.db_insert(constants.COLLECTION_COURSES_EDITIONS, result)
            raise gen.Return(True)
        else:
            yield self.db_remove(constants.COLLECTION_COURSES_EDITIONS, constants.MONGO_ID, self.user_id)
            yield self.db_insert(constants.COLLECTION_COURSES_EDITIONS, result)
            raise gen.Return(False)

    @gen.coroutine
    def __build_terms(self):
        terms = yield self.db_terms(self.user_id)
        for term_id in terms:
            term_doc = yield self.db_term(term_id, self.usos_id)
            if term_doc:
                continue

            try:
                result = yield self.usos_term(term_id, self.usos_id)

                yield self.db_insert(constants.COLLECTION_TERMS, result)
            except UsosClientError, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __build_course_edition(self):
        courses_editions = yield self.db_courses_editions(self.user_id)
        for course_edition in courses_editions:
            course_edition_doc = yield self.db_course_edition(self.user_id, course_edition[1], course_edition[0],
                                                              self.usos_id)
            if course_edition_doc:
                continue
            try:
                result = yield self.usos_course_edition(course_edition[1], course_edition[0], self.user_id, self.usos_id, fetch_participants=True)
                yield self.db_insert(constants.COLLECTION_COURSE_EDITION, result)
            except UsosClientError, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    # @gen.coroutine
    # def __build_courses(self, client, usos, crawl_time):
    #
    #     courses = list()
    #     courses_editions = list()
    #     existing_courses_editions = list()
    #
    #     # get courses that exists in mongo and remove from list to fetch
    #     existing_courses = self.dao.get_courses(usos[constants.USOS_ID], constants.COURSE_ID)
    #
    #     # get courses from course_edition
    #     for ce in self.dao.get_usos_course_edition(usos[constants.USOS_ID]):
    #         if ce[constants.COURSE_ID] not in existing_courses:
    #             existing_courses.append(ce[constants.COURSE_ID])
    #             courses.append(ce[constants.COURSE_ID])
    #         if {ce[constants.COURSE_ID]: ce[constants.TERM_ID]} not in existing_courses_editions:
    #             existing_courses_editions.append({ce[constants.COURSE_ID]: ce[constants.TERM_ID]})
    #             courses_editions.append({ce[constants.COURSE_ID]: ce[constants.TERM_ID]})
    #
    #     # get courses_editions conducted by all lecturers
    #     for course_conducted in self.dao.get_courses_conducted_by_lecturers(usos[constants.USOS_ID]):
    #         if len(course_conducted['course_editions_conducted']) > 0:
    #             for courseedition in course_conducted['course_editions_conducted']:
    #                 course_id, term_id = courseedition['id'].split('|')
    #                 if course_id not in existing_courses:
    #                     existing_courses.append(course_id)
    #                     courses.append(course_id)
    #                 if {course_id: term_id} not in existing_courses_editions:
    #                     existing_courses_editions.append({course_id: term_id})
    #                     courses_editions.append({course_id: term_id})
    #
    #     # get courses from course_edition
    #     for course in courses:
    #         try:
    #             result = client.course(course)
    #         except UsosClientError, ex:
    #             self._exc(ex)
    #             continue
    #
    #         if result:
    #             result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
    #             self.dao.insert(constants.COLLECTION_COURSES, result)
    #         else:
    #             logging.warn("no course for course_id: %r.", course)
    #
    #             # wylaczamy sciaganie reszty
    #             # users_to_fetch = list()
    #             # # get course_edition for lecturers
    #             # if len(courses_editions) > 0:
    #             #     for ca in courses_editions:
    #             #         for course_id, term_id in ca.items():
    #             #             continue
    #             #         try:
    #             #             result = client.course_edition(course_id, term_id)
    #             #         except UsosClientError, ex:
    #             #             self._exc(ex)
    #             #             continue
    #             #
    #             #         if result:
    #             #             result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
    #             #             self.dao.insert(constants.COLLECTION_COURSE_EDITION, result)
    #             #         else:
    #             #             logging.warn("no course_edition for course_id: %r term_id: %r", course_id, term_id)
    #             #
    #             #         # get lecturers for rest of given course_edition
    #             #         # self.__find_users_related(users_to_fetch, result)
    #             # self.__build_users_info(client, crawl_time, users_to_fetch, usos)

    @gen.coroutine
    def __build_faculties(self):
        faculties = yield self.db_faculties_from_courses(self.usos_id)

        for faculty_id in faculties:
            faculty_doc = yield self.db_faculty(faculty_id, self.usos_id)
            if faculty_doc:
                continue  # faculty already exists

            try:
                result = yield self.usos_faculty(faculty_id, self.usos_id)

                if result:
                    yield self.db_insert(constants.COLLECTION_FACULTIES, result)
                else:
                    logging.warn("no faculty for fac_id: {0} and usos_id: {1)".format(faculty_id, self.usos_id))
            except UsosClientError, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __build_users_info(self, user_info_ids):
        for user_info_id in user_info_ids:
            user_info_doc = yield self.db_users_info(user_info_id, self.usos_id)
            if user_info_doc:
                yield self.__build_user_info(user_info_id)
                yield self.__build_programmes(user_info_id)

        raise gen.Return(None)

    @gen.coroutine
    def __build_units(self, units):

        for unit_id in units:
            unit_doc = yield self.db_unit(unit_id, self.usos_id)
            if unit_doc:
                continue  # units already exists

            try:
                result = yield self.usos_unit(unit_id, self.usos_id)
                if result:
                    yield self.db_insert(constants.COLLECTION_COURSES_UNITS, result)
                else:
                    logging.warn("no unit for unit_id: {0} and usos_id: {1)".format(unit_id, self.usos_id))
            except UsosClientError, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __build_groups(self, groups):

        for group_id in groups:
            group_doc = yield self.db_group(group_id, self.usos_id)
            if group_doc:
                continue  # group already exists

            try:
                result = yield self.usos_group(group_id, self.usos_id)
                if result:
                    yield self.db_insert(constants.COLLECTION_GROUPS, result)
                else:
                    logging.warn("no group for group_id: {0} and usos_id: {1)".format(group_id, self.usos_id))
            except UsosClientError, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __process_user_data(self):
        units_found = list()
        courses_editions = yield self.db_courses_editions(self.user_id)

        for data in courses_editions:
            term_id, course_id = data[0], data[1]

            try:
                result = yield self.usos_course_edition(course_id, term_id, self.user_id, self.usos_id, fetch_participants=True)
                yield self.db_insert(constants.COLLECTION_COURSE_EDITION, result)

                # collect units
                if result and 'course_units_ids' in result:
                    for unit in result['course_units_ids']:
                        if unit not in units_found:
                            units_found.append(unit)

                    grade_doc = yield self.db_grades(course_id, term_id, self.user_id, self.usos_id)
                    if grade_doc:
                        continue  # grades for course and term already exists

                if result and (
                            result['grades']['course_grades'] or result['grades']['course_units_grades']):
                    yield self.db_insert(constants.COLLECTION_GRADES, result)
                else:
                    logging.warn(
                        'grades not found for course_id: {0} term_id: {1} usos_id: {2} and user_id: {3}'.format(
                            course_id, term_id, self.usos_id, self.user_id
                        ))
            except UsosClientError, ex:
                yield self._exc(ex)

        yield self.__build_units(units_found)
        yield self.__build_groups(units_found)

        raise gen.Return(None)

    @staticmethod
    def __find_users_related(users, result):
        if result and 'participants' in result:
            participants = result.pop('participants')
            for p in participants:
                if p not in users:
                    users.append(p)

        if result and 'lecturers' in result:
            lecturers = result.pop('lecturers')
            for l in lecturers:
                if l not in users:
                    users.append(l)

    @gen.coroutine
    def initial_user_crawl(self, user_id):
        try:
            self._user_doc = yield self.db_get_user(user_id)
            if not self.user_doc:
                raise CrawlerException("Initial crawler not started. Unknown user with id: %r.", user_id)

            self._usos_doc = yield self.db_get_usos(self.user_doc[constants.USOS_ID])

            user_info_id = yield self.__build_user_info()
            yield self.__subscribe()

            monday = self.__get_monday()
            yield self.__build_time_table(monday)
            yield self.__build_time_table(self.__get_next_monday(monday))
            yield self.__build_programmes(user_info_id)
            yield self.__build_curses_editions()
            yield self.__build_terms()
            yield self.__build_course_edition()
            yield self.__process_user_data()

            # # do przeróbki niech działa nie na kursach tylko programach i przemieniesie nad programy
            yield self.__build_faculties()

            # # wyłączamy ściąganie  dla wszystkich
            # self.__build_courses(client, usos, crawl_time)

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

                courses_editions = yield self.__build_curses_editions()
                if courses_editions:
                    # self.__build_terms()
                    yield self.__build_course_edition()
                    yield self.__process_user_data()
                    # self.__build_courses(client, usos, crawl_time)
                    yield self.__build_faculties()
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

            yield self.__build_course_editions_conducted(courses_conducted)
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
                self.__build_time_table(monday)
                self.__build_time_table(next_monday)

                logging.debug('updating time table for user: {0}'.format(user_doc[constants.MONGO_ID]))
            except Exception, ex:
                yield self._exc(ex)

    @gen.coroutine
    def unsubscribe(self, user_id):
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            self._user_doc = yield self.db_archive_user(user_id)

            if not self.user_doc:
                raise CrawlerException(
                    "Unsubscribe process not started. Unknown user with id: %r or user not paired with any USOS",
                    user_id)

            self._usos_doc = yield self.db_get_usos(self.user_doc[constants.USOS_ID])

            if constants.USOS_ID in self.user_doc:
                client = yield self.usos_client()
                try:
                    client.unsubscribe()
                except UsosClientError, ex:
                    yield self._exc(ex)

        except Exception, ex:
            yield self._exc(ex)

    @gen.coroutine
    def notifier_status(self):
        try:
            usosAsync = UsosAsync()
            timestamp = datetime.now()

            usoses = yield self.db_usoses()
            for usos in usoses:
                try:
                    data = yield usosAsync.notifier_status(usos[constants.USOS_URL])
                    data[constants.CREATED_TIME] = timestamp
                    data[constants.USOS_ID] = usos[constants.USOS_ID]

                    yield self.db_insert(constants.COLLECTION_NOTIFIER_STATUS, data)
                except UsosClientError, ex:
                    yield self._exc(ex)

        except Exception, ex:
            self._exc(ex)


@gen.coroutine
def main():
    crawler = UsosCrawler()
    user_id = '5737651dd54c4b09142cf68a'
    yield crawler.initial_user_crawl(user_id)
    # yield crawler.daily_crawl()
    # yield crawler.update_user_crawl(user_id)
    # yield crawler.update_time_tables()


if __name__ == '__main__':
    from tornado import ioloop
    from tornado.options import parse_command_line

    parse_command_line()
    logging.getLogger().setLevel(logging.DEBUG)
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
