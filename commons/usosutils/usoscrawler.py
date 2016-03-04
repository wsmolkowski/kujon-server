import logging
from datetime import datetime
from datetime import timedelta, date

import tornado.gen
from bson.objectid import ObjectId

import usosinstances
from commons import constants
from commons.helpers import log_execution_time
from commons.mongo_dao import Dao
from commons.usosutils.usosasync import UsosAsync
from commons.usosutils.usosclient import UsosClient
from commons.AESCipher import AESCipher

class UsosCrawler:
    def __init__(self, dao=None):
        if not dao:
            self.dao = Dao()
        else:
            self.dao = dao

        self.aes = AESCipher()
        self.usosAsync = UsosAsync()

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

    @tornado.gen.coroutine
    def recreate_dictionaries(self):

        recreate_time = datetime.now()

        self.dao.drop_collection(constants.COLLECTION_COURSES_CLASSTYPES)
        for usos in self.dao.get_usoses():
            logging.info(u"recreating dictionaries in collections {0} for {1}".format(
                    constants.COLLECTION_COURSES_CLASSTYPES,
                    usos[constants.USOS_ID]))
            inserts = list()
            class_types = yield self.usosAsync.get_courses_classtypes(usos[constants.USOS_URL])
            if len(class_types) > 0:
                for class_type in class_types.values():
                    class_type[constants.USOS_ID] = usos[constants.USOS_ID]
                    class_type[constants.CREATED_TIME] = recreate_time
                    class_type[constants.UPDATE_TIME] = recreate_time
                    inserts.append(class_type)
                self.dao.insert(constants.COLLECTION_COURSES_CLASSTYPES, inserts)
                logging.debug(
                    u"dictionary course classtypes for usos {0} inserted.".format(usos[constants.USOS_ID]))
            else:
                raise Exception(u"fail to recreate_dictionaries {0} for {1}".format(
                    constants.COLLECTION_COURSES_CLASSTYPES, usos[constants.USOS_ID]))
        raise tornado.gen.Return(True)

    def drop_collections(self):
        self.dao.drop_collections()

    @log_execution_time
    def recreate_usos(self):
        self.dao.drop_collection(constants.COLLECTION_USOSINSTANCES)
        for usos in usosinstances.USOSINSTANCES:
            logging.info('adding usos: {0} '.format(usos[constants.USOS_ID]))
            doc = self.dao.find_usos(usos[constants.USOS_ID])
            if not doc:
                self.dao.insert(constants.COLLECTION_USOSINSTANCES, self.aes.encrypt_usos(usos))

    def __build_user_info_photo(self, client, user_id, user_info_id, crawl_time, usos):
        if not self.dao.get_users_info_photo(user_info_id, usos[constants.USOS_ID]):
            photo = client.user_info_photo(user_info_id)
            if photo:
                photo = self.append(photo, usos[constants.USOS_ID], crawl_time, crawl_time)
                photo_doc = self.dao.insert(constants.COLLECTION_PHOTOS, photo)
                return photo_doc
                logging.debug(u"photo for user_id: {0} inserted {1}".format(photo[constants.USER_ID], photo_doc))
            else:
                logging.debug(u"no photo for user_id: {0}".format(user_id))

    def __build_user_info(self, client, user_id, user_info_id, crawl_time, usos):

        result = client.user_info(user_info_id)
        result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
        if user_id:
            result[constants.USER_ID] = user_id

        # if user has photo - download
        if 'has_photo' in result and result['has_photo']:
            result['has_photo'] = self.__build_user_info_photo(client, user_id, result[constants.USER_INFO_ID], crawl_time, usos)

        ui_doc = self.dao.insert(constants.COLLECTION_USERS_INFO, result)
        logging.debug(u"user_info inserted: {0}".format(ui_doc))


        # if user conducts courses - fetch courses
        if result['course_editions_conducted']:
            self.__build_course_editions_for_conducted(client, result['course_editions_conducted'], crawl_time, result, usos)

        return result[constants.USER_INFO_ID]

    def __build_course_editions_for_conducted(self, client, courses_conducted, crawl_time, result, usos):
        for courseterm in courses_conducted:
            course_id, term_id = courseterm['id'].split('|')
            course_doc = self.dao.get_course_edition(course_id, term_id, usos[constants.USOS_ID])
            if course_doc:
                continue
            else:
                course_result = client.course_edition(course_id, term_id, fetch_participants=False)
                course_result = self.append(course_result, usos[constants.USOS_ID], crawl_time, crawl_time)
                course_doc = self.dao.insert(constants.COLLECTION_COURSE_EDITION, course_result)
                logging.debug(
                    u"course_edition for course_id: {0} term_id: {1} inserted: {2}".format(course_id, term_id,
                                                                                           course_doc))

    def __build_tt(self, client, user_id, crawl_time, usos, given_date):

        tts = self.dao.get_user_tt(user_id, usos[constants.USOS_ID], given_date)
        if tts:
            for tt in tts:
                pass
                # TODO: sprawdzenie czy istnieja grypy
                # w zaleznosci od typu:
                # If type equals "classgroup":
                # If type equals "meeting":
                # If type equals "exam":
        else:
            try:
                result = client.tt(given_date)
                tt = dict()
                tt[constants.USOS_ID] = usos[constants.USOS_ID]
                tt[constants.TT_STARTDATE] = str(given_date)
                tt['tts'] = result
                tt[constants.USER_ID] = user_id
                tt_doc = self.dao.insert(constants.COLLECTION_TT,tt)
                if result:
                    logging.debug(u"time tables for date: {0} inserted: {1}".format(given_date, tt_doc))
                else:
                    logging.debug(u"no time tables for date: {0} inserted empty".format(given_date))
            except Exception, ex:
                logging.debug(u"problem during tt fetch: {0}".format(ex.message))

    def __build_programmes(self, client, user_info_id, crawl_time, usos):

        programmes = self.dao.get_users_info_programmes(user_info_id, usos[constants.USOS_ID])
        for programme in programmes:
            # checing if program exists in mongo
            if self.dao.get_programme(programme['programme']['id'], usos[constants.USOS_ID]):
                continue
            else:
                result = client.programme(programme['programme']['id'])
                if result:
                    result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                    result[constants.PROGRAMME_ID] = result.pop('id')
                    prog_doc = self.dao.insert(constants.COLLECTION_PROGRAMMES, result)
                    logging.debug(u"programme {0} inserted: {1}".format(programme['id'], prog_doc))
                else:
                    logging.debug(u"no programme: {0}.".format(programme['id']))

    def __build_curseseditions(self, client, crawl_time, user_id, usos):

        result = client.courseeditions_info()
        if result:
            result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
            result[constants.USER_ID] = user_id
            ce_doc = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
            logging.debug(u"course_editions for user_id: {0} inserted: {1}".format(user_id, ce_doc))
        else:
            logging.debug(u"no course_editions for user_id: {0".format(user_id))

    @tornado.gen.coroutine
    def __build_terms(self, user_id, usos, crawl_time):

        for term_id in self.dao.get_user_terms(user_id):

            if self.dao.get_term(term_id, usos[constants.USOS_ID]):
                continue  # term already exists
            result = yield self.usosAsync.get_term_info(usos[constants.USOS_URL], term_id)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                t_doc = self.dao.insert(constants.COLLECTION_TERMS, result)
                logging.debug(u"terms for term_id: {0} inserted {1}".format(term_id, t_doc))
            else:
                logging.debug(u"no terms for term_id: {0}.".format(term_id))

    @tornado.gen.coroutine
    def __build_course_edition(self, client, user_id, usos, crawl_time):

        for course_edition in self.dao.get_user_courses(user_id, usos[constants.USOS_ID]):
            if self.dao.get_course(course_edition[constants.COURSE_ID], usos[constants.USOS_ID]):
                continue  # course already exists
            result = None
            try:
                result = client.course_edition(course_edition[constants.COURSE_ID], course_edition[constants.TERM_ID], fetch_participants=True)
            except Exception, ex:
                logging.debug(u"problem during course_edition fetch.".format(ex.message))
            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                c_doc = self.dao.insert(constants.COLLECTION_COURSE_EDITION, result)
                logging.debug(u"course_edition for course_id: {0} term_id: {1} inserted {2}".format(course_edition[
                            constants.COURSE_ID], course_edition[constants.TERM_ID], c_doc))
            else:
                logging.debug(u"no course_edition for course_id: {0} term_id: {1}.".format(course_edition[
                            constants.COURSE_ID], course_edition[constants.TERM_ID]))

    @tornado.gen.coroutine
    def __build_courses(self, client, user_id, usos, crawl_time):

        courses = list()
        for course_edition in self.dao.get_courses_editions(user_id, usos[constants.USOS_ID]):
            for term in course_edition['course_editions']:
                for course in course_edition['course_editions'][term]:
                    courses.append(course[constants.COURSE_ID])

        # get courses that exists in mongo and remove from list to fetch
        if courses:
            for existing_course in self.dao.get_courses(courses, usos[constants.USOS_ID]):
                courses.remove(existing_course[constants.COURSE_ID])

        # get the rest of courses on course list from usos
        if courses:
            for course in courses:
                result = client.course(course)
                if result:
                    result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                    result[constants.COURSE_ID] = result.pop('id')
                    c_doc = self.dao.insert(constants.COLLECTION_COURSES, result)
                    logging.debug(u"course for course_id: {0} inserted {1}".format(course, c_doc))
                else:
                    logging.debug(u"no course for course_id: {0}.".format(course))

    @tornado.gen.coroutine
    def __build_faculties(self, client, usos, crawl_time):
        for faculty in self.dao.get_faculties_from_courses(usos[constants.USOS_ID]):
            if self.dao.get_faculty(faculty, usos[constants.USOS_ID]):
                continue  # fac already exists

            result = client.faculty(faculty)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.FACULTY_ID] = faculty
                fac_doc = self.dao.insert(constants.COLLECTION_FACULTIES, result)
                logging.debug(u"faculty for fac_id: {0} inserted {1}".format(faculty, fac_doc))
            else:
                logging.debug(u"no faculty for fac_id: {0}.".format(faculty))

    @tornado.gen.coroutine
    def __build_user_info_for_users(self, client, crawl_time, users, usos):
        for user in users:
            if not self.dao.get_users_info_by_usos_id(user['id'], usos):
                self.__build_user_info(client, None, user['id'], crawl_time, usos)
                logging.debug(u"Fetched user_info for user with id: {0}".format(user['id']))

                # build programme for gven user
                self.__build_programmes(client, user['id'], crawl_time,usos)

    @tornado.gen.coroutine
    def __build_units(self, client, crawl_time, units, usos):

        for unit_id in units:
            if self.dao.get_units(unit_id, usos[constants.USOS_ID]):
                continue  # units already exists

            result = client.units(unit_id)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.UNIT_ID] = result.pop('id')
                u_doc = self.dao.insert(constants.COLLECTION_COURSES_UNITS, result)
                logging.debug(u"unit {0} inserted {1}.".format(unit_id, u_doc))
            else:
                logging.debug(u"no unit {0}.".format(unit_id))

    @tornado.gen.coroutine
    def __build_groups(self, client, crawl_time, units, usos):

        for unit in units:
            try:
                result = client.groups(unit)
            except Exception, ex:
                logging.exception(u"exception during fetch unit: {0} : {1}".format(unit, ex.message))
            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                grp_doc = self.dao.insert(constants.COLLECTION_GROUPS, result)
                logging.debug(u"group for unit: {0} inserted: {1}".format(unit, grp_doc))
            else:
                logging.debug(u"no group for unit: {0}.".format(unit))

    @tornado.gen.coroutine
    def __build_grades_participants_lecturers_units_groups(self, client, user_id, usos, crawl_time):

        all_participants = list()
        all_lecturers = list()
        all_units = list()
        for data in self.dao.get_user_courses_editions(user_id):
            term_id, course_id = data[0], data[1]

            # participants ane lectures
            result = None
            try:
                result = client.course_edition(course_id, term_id, fetch_participants=True)
            except Exception, ex:
                logging.exception(u"problem during course_edition fetch: {0}.".format(ex.message))
            if result and 'participants' in result:
                participants = result.pop('participants')
                lecturers = result.pop('lecturers')
                for p in participants:
                    if p not in all_participants:
                        all_participants.append(p)
                for l in lecturers:
                    if l not in all_lecturers:
                        all_lecturers.append(l)

            # units
            if result and 'course_units_ids' in result:
                units = result.pop('course_units_ids')
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.USER_ID] = user_id
                if self.dao.get_grades(course_id, term_id, user_id, usos[constants.USOS_ID]):
                    continue  # grades for course and term already exists
                for unit in units:
                    if unit not in all_units:
                        all_units.append(unit)

            # grades
            if result:
                g_doc = self.dao.insert(constants.COLLECTION_GRADES, result)
                logging.debug(
                    u"grades for course_id: {0} and term_id: {1} inserted {2}".format(course_id, term_id, g_doc))

        self.__build_user_info_for_users(client, crawl_time, all_participants, usos)
        self.__build_user_info_for_users(client, crawl_time, all_lecturers, usos)

        self.__build_units(client, crawl_time, all_units, usos)
        self.__build_groups(client, crawl_time, all_units, usos)

    @log_execution_time
    @tornado.gen.coroutine
    def initial_user_crawl(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        crawl_time = datetime.now()

        user = self.dao.get_user(user_id)
        if not user:
            logging.error(u"Could not crawl for usos data for unknown user with id: {0}.".format(user_id))
            return

        usos = self.dao.get_usos(user[constants.USOS_ID])

        client = UsosClient(usos[constants.USOS_URL], usos[constants.CONSUMER_KEY],
                            usos[constants.CONSUMER_SECRET],
                            user[constants.ACCESS_TOKEN_KEY], user[constants.ACCESS_TOKEN_SECRET])
        try:
            user_info_id = self.__build_user_info(client, user_id, None, crawl_time, usos)

            # fetch tt for current and next week
            today = date.today()
            monday = today - timedelta(days=(today.weekday()) % 7)
            next_monday = monday + timedelta(days=7)
            self.__build_tt(client, user_id, crawl_time, usos, monday)
            self.__build_tt(client, user_id, crawl_time, usos, next_monday)

            self.__build_programmes(client, user_info_id, crawl_time, usos)

            self.__build_curseseditions(client, crawl_time, user_id, usos)

            yield self.__build_terms(user_id, usos, crawl_time)

            self.__build_course_edition(client, user_id, usos, crawl_time)

            yield self.__build_grades_participants_lecturers_units_groups(client, user_id, usos, crawl_time)

            self.__build_courses(client, user_id, usos, crawl_time)

            self.__build_faculties(client, usos, crawl_time)

            # crawl collection
            result = self.append(dict(), usos[constants.USOS_ID], crawl_time, crawl_time)
            result[constants.USER_ID] = user_id
            result[constants.CRAWL_TYPE] = constants.CRAWL_TYPE_INITIAL
            doc = self.dao.insert(constants.COLLECTION_CRAWLLOG, result)
            logging.info(u"crawl log inserted with id {0}".format(doc))

        except Exception, ex:
            logging.exception(u"Exception while initial user usos crawler: {0}".format(ex.message))
