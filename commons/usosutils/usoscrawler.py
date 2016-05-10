import logging
import traceback
from datetime import datetime
from datetime import timedelta, date

from bson.objectid import ObjectId
from tornado import gen
from tornado.concurrent import run_on_executor, futures

from commons import constants, utils
from commons.AESCipher import AESCipher
from commons.Dao import Dao
from commons.errors import UsosClientError
from commons.usosutils.usosasync import UsosAsync
from commons.usosutils.usosclient import UsosClient


class UsosCrawler(object):
    EXCEPTION_TYPE = 'usoscrawler'
    EVENT_TYPES = ['crstests/user_grade', 'grades/grade', 'crstests/user_point']

    def __init__(self, dao=None):
        if not dao:
            self.dao = Dao()
        else:
            self.dao = dao

        self.aes = AESCipher()
        self.executor = futures.ThreadPoolExecutor(constants.WORKERS_MAX)

    @staticmethod
    def append(data, usos_id, create_time, update_time):
        if not data:
            data = dict()

        if usos_id:
            data[constants.USOS_ID] = usos_id

        if create_time:
            data[constants.CREATED_TIME] = create_time

        if update_time:
            data[constants.UPDATE_TIME] = update_time

        return data

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

            self.dao.insert(constants.COLLECTION_EXCEPTIONS, utils.serialize(exc_doc))
            logging.error(exc_doc)
        except Exception, ex:
            logging.exception(ex)

    def __build_user_info_photo(self, client, user_id, user_info_id, crawl_time, usos):
        if not self.dao.get_users_info_photo(user_info_id, usos[constants.USOS_ID]):

            try:
                photo = client.user_info_photo(user_info_id)
            except UsosClientError, ex:
                self._exc(ex)
                return

            if photo:
                photo = self.append(photo, usos[constants.USOS_ID], crawl_time, crawl_time)
                photo_doc = self.dao.insert(constants.COLLECTION_PHOTOS, photo)
                return photo_doc
            else:
                logging.warn("no photo for user_id: %r", user_id)

    @run_on_executor
    def __build_user_info(self, client, user_id, user_info_id, crawl_time, usos):
        if user_id and self.dao.get_users_info_by_user_id(user_id, usos):
            logging.debug("not building user info - it already exists for %r", user_id)
            return

        try:
            result = client.user_info(user_info_id)
        except UsosClientError, ex:
            self._exc(ex)
            return

        result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
        if user_id:
            result[constants.USER_ID] = user_id

        # if user has photo - download
        if 'has_photo' in result and result['has_photo']:
            result['has_photo'] = self.__build_user_info_photo(client, user_id, result[constants.ID],
                                                               crawl_time, usos)

        # strip english values and if value is empty change to None
        result['office_hours'] = result['office_hours']['pl']
        result['interests'] = result['interests']['pl']

        # strip empty values
        if result['homepage_url'] and result['homepage_url'] == "":
            result['homepage_url'] = None

        # strip english names from programmes description
        for programme in result['student_programmes']:
            programme['programme']['description'] = programme['programme']['description']['pl']

        self.dao.insert(constants.COLLECTION_USERS_INFO, result)

        # if user conducts courses - fetch courses
        if result['course_editions_conducted']:
            self.__build_course_editions_for_conducted(client, result['course_editions_conducted'], crawl_time, usos)

        return result[constants.ID]

    def __build_course_editions_for_conducted(self, client, courses_conducted, crawl_time, usos):
        for courseterm in courses_conducted:
            course_id, term_id = courseterm[constants.ID].split('|')
            course_doc = self.dao.get_course_edition(course_id, term_id, usos[constants.USOS_ID])
            if course_doc:
                continue

            try:
                course_result = client.course_edition(course_id, term_id, fetch_participants=False)
            except UsosClientError, ex:
                self._exc(ex)
                continue

            course_result = self.append(course_result, usos[constants.USOS_ID], crawl_time, crawl_time)
            self.dao.insert(constants.COLLECTION_COURSE_EDITION, course_result)

    @run_on_executor
    def __subscribe(self, client, user_id, usos):
        for event_type in self.EVENT_TYPES:
            try:
                subscribe_doc = client.subscribe(event_type, str(user_id))
                subscribe_doc = self.append(subscribe_doc, usos[constants.USOS_ID], datetime.now(), datetime.now())
                subscribe_doc[constants.USER_ID] = user_id
                subscribe_doc['event_type'] = event_type
                self.dao.insert(constants.COLLECTION_SUBSCRIPTION, subscribe_doc)
            except UsosClientError, ex:
                self._exc(ex)
                continue

    @run_on_executor
    def __build_time_table(self, client, user_id, usos_id, given_date):
        # existing_tt = self.dao.get_time_table(user_id, usos_id)
        try:
            result = client.time_table(given_date)
        except UsosClientError, ex:
            self._exc(ex)
            return

        if result:
            tt = dict()
            tt[constants.USOS_ID] = usos_id
            tt[constants.TT_STARTDATE] = str(given_date)
            tt['tts'] = result
            tt[constants.USER_ID] = user_id
            self.dao.insert(constants.COLLECTION_TT, tt)

            # if existing_tt:
            #     self.dao.remove(constants.COLLECTION_TT, existing_tt)
        else:
            logging.debug("no time tables for date: %r inserted empty", given_date)

    @run_on_executor
    def __build_programmes(self, client, user_info_id, crawl_time, usos):

        for programme in self.dao.get_users_info_programmes(user_info_id, usos[constants.USOS_ID]):
            # checking if program exists in mongo
            if self.dao.get_programme(programme['programme'][constants.ID], usos[constants.USOS_ID]):
                continue

            try:
                result = client.programme(programme['programme'][constants.ID])
            except UsosClientError, ex:
                self._exc(ex)
                continue

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.PROGRAMME_ID] = result.pop(constants.ID)

                # strip english names
                result['name'] = result['name']['pl']
                result['mode_of_studies'] = result['mode_of_studies']['pl']
                result['level_of_studies'] = result['level_of_studies']['pl']
                result['duration'] = result['duration']['pl']
                if 'faculty' in result and 'name' in result['faculty']:
                    result['faculty']['name'] = result['faculty']['name']['pl']
                    result['faculty'][constants.FACULTY_ID] = result['faculty']['id']
                    del (result['faculty']['id'])

                self.dao.insert(constants.COLLECTION_PROGRAMMES, result)
            else:
                logging.warn("no programme: %r.", programme[constants.ID])

    @run_on_executor
    def __build_curseseditions(self, client, crawl_time, user_id, usos):

        update = False
        course_edition = self.dao.get_courses_editions(user_id, usos[constants.USOS_ID])
        if course_edition:
            update = True

        try:
            result = client.courseeditions_info()
        except UsosClientError, ex:
            self._exc(ex)
            return

        if result:
            result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
            result[constants.USER_ID] = user_id

            # checking if update differs from version from mango

            if update:
                try:
                    compare = cmp(result[constants.COURSE_EDITIONS], course_edition[constants.COURSE_EDITIONS])
                except Exception, ex:
                    compare = 1
                    logging.exception("Could not find compare old and new courseedition: %r", ex.message)
                if compare == 0:
                    logging.debug("course_editions not changed.")
                    return False
                else:
                    logging.debug("course_editions changed - updating and moving old to archive.")
                    self.dao.insert(constants.COLLECTION_COURSES_EDITIONS_ARCHIVE, course_edition)
                    self.dao.remove(constants.COLLECTION_COURSES_EDITIONS, constants.MONGO_ID,
                                    course_edition[constants.MONGO_ID])
            self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
            return True
        else:
            logging.warn("no course_editions for user_id: %r in USOS.", user_id)
            return False

    @run_on_executor
    def __build_terms(self, client, user_id, usos, crawl_time):

        for term_id in self.dao.get_user_terms(user_id):

            if self.dao.get_term(term_id, usos[constants.USOS_ID]):
                continue

            try:
                result = client.get_term_info(term_id)
            except UsosClientError, ex:
                self._exc(ex)
                continue

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.TERM_ID] = result.pop(constants.ID)
                self.dao.insert(constants.COLLECTION_TERMS, result)
            else:
                logging.warn("no term_id: %r found!", term_id)

    @run_on_executor
    def __build_course_edition(self, client, user_id, usos, crawl_time):

        for course_edition in self.dao.get_user_courses(user_id, usos[constants.USOS_ID]):
            existing_doc = self.dao.get_course_edition(course_edition[constants.COURSE_ID],
                                                       course_edition[constants.TERM_ID], usos[constants.USOS_ID])

            if existing_doc:
                continue

            try:
                result = client.course_edition(course_edition[constants.COURSE_ID], course_edition[constants.TERM_ID],
                                               fetch_participants=True)
            except UsosClientError, ex:
                self._exc(ex)
                continue

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                self.dao.insert(constants.COLLECTION_COURSE_EDITION, result)

                if existing_doc:
                    self.dao.delete_doc(constants.COLLECTION_COURSE_EDITION, existing_doc[constants.MONGO_ID])
            else:
                logging.warn("no course_edition for course_id: %r term_id: %r", course_edition[
                    constants.COURSE_ID], course_edition[constants.TERM_ID])

    @run_on_executor
    def __build_courses_and_rest_of_existing_courses(self, client, usos, crawl_time):

        courses = list()
        courses_editions = list()
        existing_courses_editions = list()

        # get courses that exists in mongo and remove from list to fetch
        existing_courses = self.dao.get_courses(usos[constants.USOS_ID], constants.COURSE_ID)

        # get courses from course_edition
        for ce in self.dao.get_usos_course_edition(usos[constants.USOS_ID]):
            if ce[constants.COURSE_ID] not in existing_courses:
                existing_courses.append(ce[constants.COURSE_ID])
                courses.append(ce[constants.COURSE_ID])
            if {ce[constants.COURSE_ID]: ce[constants.TERM_ID]} not in existing_courses_editions:
                existing_courses_editions.append({ce[constants.COURSE_ID]: ce[constants.TERM_ID]})
                courses_editions.append({ce[constants.COURSE_ID]: ce[constants.TERM_ID]})

        # get courses_editions conducted by all lecturers
        for course_conducted in self.dao.get_courses_conducted_by_lecturers(usos[constants.USOS_ID]):
            if len(course_conducted['course_editions_conducted']) > 0:
                for courseedition in course_conducted['course_editions_conducted']:
                    course_id, term_id = courseedition['id'].split('|')
                    if course_id not in existing_courses:
                        existing_courses.append(course_id)
                        courses.append(course_id)
                    if {course_id: term_id} not in existing_courses_editions:
                        existing_courses_editions.append({course_id: term_id})
                        courses_editions.append({course_id: term_id})

        # get courses from course_edition
        for course in courses:
            try:
                result = client.course(course)
            except UsosClientError, ex:
                self._exc(ex)
                continue

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                self.dao.insert(constants.COLLECTION_COURSES, result)
            else:
                logging.warn("no course for course_id: %r.", course)

        users_to_fetch = list()
        # get course_edition for lecturers
        if len(courses_editions) > 0:
            for ca in courses_editions:
                for course_id, term_id in ca.items():
                    continue
                try:
                    result = client.course_edition(course_id, term_id)
                except UsosClientError, ex:
                    self._exc(ex)
                    continue

                if result:
                    result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                    self.dao.insert(constants.COLLECTION_COURSE_EDITION, result)
                else:
                    logging.warn("no course_edition for course_id: %r term_id: %r", course_id, term_id)

                # get lecturers for rest of given course_edition
                self.__find_users_related(users_to_fetch, result)
        self.__build_users_info(client, crawl_time, users_to_fetch, usos)

    @run_on_executor
    def __build_faculties(self, client, usos, crawl_time):
        for faculty in self.dao.get_faculties_from_courses(usos[constants.USOS_ID]):
            if self.dao.get_faculty(faculty, usos[constants.USOS_ID]):
                continue  # fac already exists

            try:
                result = client.faculty(faculty)
            except UsosClientError, ex:
                self._exc(ex)
                continue

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.FACULTY_ID] = faculty
                result['name'] = result['name']['pl']
                self.dao.insert(constants.COLLECTION_FACULTIES, result)
            else:
                logging.warn("no faculty for fac_id: %r.", faculty)

    @run_on_executor
    def __build_users_info(self, client, crawl_time, user_info_ids, usos_id):
        for user_info_id in user_info_ids:
            if not self.dao.get_users_info(user_info_id[constants.ID], usos_id):
                # build user_info
                yield self.__build_user_info(client, None, user_info_id[constants.ID], crawl_time, usos_id)

                # build programme for given user
                yield self.__build_programmes(client, user_info_id[constants.ID], crawl_time, usos_id)

    @run_on_executor
    def __build_units(self, client, crawl_time, units, usos):

        for unit_id in units:
            if self.dao.get_units(unit_id, usos[constants.USOS_ID]):
                continue  # units already exists

            try:
                result = client.units(unit_id)
            except UsosClientError, ex:
                self._exc(ex)
                continue

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.UNIT_ID] = result.pop(constants.ID)
                self.dao.insert(constants.COLLECTION_COURSES_UNITS, result)
            else:
                logging.warn("no unit %r.", format(unit_id))

    @run_on_executor
    def __build_groups(self, client, crawl_time, units, usos):

        for unit in units:
            if self.dao.get_group(unit, usos[constants.USOS_ID]):
                continue

            try:
                result = client.groups(unit)
            except UsosClientError, ex:
                self._exc(ex)
                continue

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                self.dao.insert(constants.COLLECTION_GROUPS, result)
            else:
                logging.warn("no group for unit: %r.", unit)

    @run_on_executor
    def __process_user_data(self, client, user_id, usos, crawl_time):

        users_found = list()
        units_found = list()

        for data in self.dao.get_user_courses_editions(user_id):
            term_id, course_id = data[0], data[1]

            try:
                result = client.course_edition(course_id, term_id, fetch_participants=True)
            except UsosClientError, ex:
                self._exc(ex)
                return

            self.__find_users_related(users_found, result)

            # units
            if result and 'course_units_ids' in result:
                for unit in result['course_units_ids']:
                    if unit not in units_found:
                        units_found.append(unit)

                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.USER_ID] = user_id
                if self.dao.get_grades(course_id, term_id, user_id, usos[constants.USOS_ID]):
                    continue  # grades for course and term already exists

            if result and (
                            len(result['grades']['course_grades']) > 0 or len(
                        result['grades']['course_units_grades']) > 0):
                self.dao.insert(constants.COLLECTION_GRADES, result)

        yield self.__build_users_info(client, crawl_time, users_found, usos)
        yield self.__build_units(client, crawl_time, units_found, usos)
        yield self.__build_groups(client, crawl_time, units_found, usos)

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

    def __build_client(self, user):
        self.user = user
        usos = self.dao.get_usos(user[constants.USOS_ID])
        client = UsosClient(usos[constants.USOS_URL], usos[constants.CONSUMER_KEY],
                            usos[constants.CONSUMER_SECRET],
                            user[constants.ACCESS_TOKEN_KEY], user[constants.ACCESS_TOKEN_SECRET])
        return client, usos

    @run_on_executor
    def initial_user_crawl(self, user_id):
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            crawl_time = datetime.now()

            user = self.dao.get_user(user_id)
            if not user:
                raise Exception("Initial crawler not started. Unknown user with id: %r.", user_id)

            client, usos = self.__build_client(user)
            user_info_id = yield self.__build_user_info(client, user_id, None, crawl_time, usos)

            yield self.__subscribe(client, user_id, usos)

            # fetch time_table for current and next week
            monday = self.__get_monday()
            yield self.__build_time_table(client, user_id, usos[constants.USOS_ID], monday)
            yield self.__build_time_table(client, user_id, usos[constants.USOS_ID], self.__get_next_monday(monday))
            yield self.__build_programmes(client, user_info_id, crawl_time, usos)
            yield self.__build_curseseditions(client, crawl_time, user_id, usos)
            yield self.__build_terms(client, user_id, usos, crawl_time)
            yield self.__build_course_edition(client, user_id, usos, crawl_time)
            yield self.__process_user_data(client, user_id, usos, crawl_time)
            yield self.__build_courses_and_rest_of_existing_courses(client, usos, crawl_time)
            yield self.__build_faculties(client, usos, crawl_time)
        except Exception, ex:
            self._exc(ex)

    @gen.coroutine
    def daily_crawl(self):

        crawl_time = datetime.now()

        for user in self.dao.get_users():
            try:
                logging.debug('updating daily crawl for user: {0}'.format(user[constants.MONGO_ID]))
                client, usos = self.__build_client(user)

                # if courseseditions are updated - process update
                courses_updated = yield self.__build_curseseditions(client, crawl_time, user[constants.MONGO_ID], usos)
                if courses_updated:
                    yield self.__build_terms(client, user[constants.MONGO_ID], usos, crawl_time)
                    yield self.__build_course_edition(client, user[constants.MONGO_ID], usos, crawl_time)
                    yield self.__process_user_data(client, user[constants.MONGO_ID], usos, crawl_time)
                    yield self.__build_courses_and_rest_of_existing_courses(client, usos, crawl_time)
                    yield self.__build_faculties(client, usos, crawl_time)
            except Exception, ex:
                self._exc(ex)

    @staticmethod
    def __get_next_monday(monday):
        return monday + timedelta(days=7)

    @staticmethod
    def __get_monday():
        today = date.today()
        monday = today - timedelta(days=(today.weekday()) % 7)
        return monday

    @run_on_executor
    def update_user_crawl(self, user_id):
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            crawl_time = datetime.now()

            user = self.dao.get_user(user_id)
            if not user:
                raise Exception("Update crawler not started. Unknown user with id: %r", user_id)

            client, usos = self.__build_client(user)

            courses_conducted = self.dao.courses_conducted(user_id)

            self.__build_course_editions_for_conducted(client, courses_conducted, crawl_time, usos)
        except Exception, ex:
            self._exc(ex)

    @gen.coroutine
    def update_time_tables(self):
        monday = self.__get_monday()
        next_monday = self.__get_next_monday(monday)

        for user in self.dao.get_users():
            try:
                logging.debug(
                    'updating time table for user: {0} and monday: {1}'.format(user[constants.MONGO_ID], monday))
                client, usos = self.__build_client(user)

                self.__build_time_table(client, user[constants.MONGO_ID], user[constants.USOS_ID], monday)
                self.__build_time_table(client, user[constants.MONGO_ID], user[constants.USOS_ID], next_monday)

                logging.debug('updating time table for user: {0}'.format(user[constants.MONGO_ID]))
            except Exception, ex:
                self._exc(ex)

    @run_on_executor
    def unsubscribe(self, user_id):
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            user = self.dao.get_archive_user(user_id)
            if not user:
                logging.warn(
                    "Unsubscribe not started. Unknown user: {0} or user not paired with any USOS.".format(
                        user_id))
                return

            if constants.USOS_ID in user:
                client, usos = self.__build_client(user)
                client.unsubscribe()

        except Exception, ex:
            self._exc(ex)

    @gen.coroutine
    def notifier_status(self):
        try:
            usosAsync = UsosAsync()
            timestamp = datetime.now()

            for usos in self.dao.get_usoses():
                data = yield usosAsync.notifier_status(usos[constants.USOS_URL])
                data[constants.CREATED_TIME] = timestamp
                data[constants.USOS_ID] = usos[constants.USOS_ID]

                self.dao.insert(constants.COLLECTION_NOTIFIER_STATUS, data)
        except Exception, ex:
            self._exc(ex)
