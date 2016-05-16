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

            # if user has photo - download
            if constants.HAS_PHOTO in result and result[constants.HAS_PHOTO]:
                photo_doc = yield self.usos_photo(result[constants.ID])
                yield self.db_insert(constants.COLLECTION_PHOTOS, photo_doc)
                result[constants.HAS_PHOTO] = photo_doc[constants.MONGO_ID]

            yield self.db_insert(constants.COLLECTION_USERS_INFO, result)

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
                if result:
                    yield self.db_insert(constants.COLLECTION_COURSE_EDITION, result)

            except UsosClientError, ex:
                yield self._exc(ex)

    @gen.coroutine
    def __subscribe(self):
        client = yield self.usos_client()
        for event_type in self.EVENT_TYPES:
            try:
                subscribe_doc = client.subscribe(event_type, self.user_id)
                subscribe_doc[constants.USOS_ID] = self.usos_id
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
    def __build_courses_editions(self):

        course_edition = yield self.db_courses_editions(self.user_id)

        if not course_edition:
            result = yield self.usos_courses_editions(self.user_id, self.usos_id)
            course_edition = yield self.db_insert(constants.COLLECTION_COURSES_EDITIONS, result)
            raise gen.Return(course_edition)
        else:
            raise gen.Return(course_edition)

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
            course_id, term_id = course_edition[constants.COURSE_ID], course_edition[constants.TERM_ID]
            course_edition_doc = yield self.db_course_edition(self.user_id, course_id, term_id, self.usos_id)
            if course_edition_doc:
                continue
            try:
                result = yield self.usos_course_edition(course_edition[constants.COURSE_ID],
                                                        course_edition[constants.TERM_ID],
                                                        self.user_id, self.usos_id,
                                                        fetch_participants=True)
                if result:
                    yield self.db_insert(constants.COLLECTION_COURSE_EDITION, result)
            except UsosClientError, ex:
                yield self._exc(ex)

        raise gen.Return(None)

    @gen.coroutine
    def __build_courses(self):

        courses = list()
        existing_courses = list()
        # get courses that exists in mongo and remove from list to fetch
        existing_courses_extended = yield self.db_courses(self.usos_id)
        for c in existing_courses_extended:
            existing_courses.append(c[constants.COURSE_ID])

        # get courses from course_edition
        courses_editions = yield self.db_courses_editions(self.user_id)
        for ce in courses_editions:
            if ce[constants.COURSE_ID] not in existing_courses:
                existing_courses.append(ce[constants.COURSE_ID])
                courses.append(ce[constants.COURSE_ID])

        # get courses
        for course_id in courses:
            result = yield self.usos_course(course_id)
            if result:
                yield self.db_insert(constants.COLLECTION_COURSES, result)
            else:
                logging.warn("no course for course_id: %r.", course_id)

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
            term_id, course_id = data[constants.TERM_ID], data[constants.COURSE_ID]

            try:
                result = yield self.usos_course_edition(course_id, term_id, self.user_id, self.usos_id, fetch_participants=True)
                if result:
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

            monday = self.__get_monday()
            yield self.__build_time_table(monday)
            yield self.__build_time_table(self.__get_next_monday(monday))

            yield self.__build_programmes(user_info_id)
            yield self.__build_courses_editions()
            yield self.__build_terms()
            yield self.__build_course_edition()
            yield self.__process_user_data()
            yield self.__build_courses()
            yield self.__build_faculties()
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

                courses_editions = yield self.__build_courses_editions()
                if courses_editions:
                    yield self.__build_course_edition()
                    yield self.__process_user_data()
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

