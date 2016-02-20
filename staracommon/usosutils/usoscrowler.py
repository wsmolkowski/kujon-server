import logging
from datetime import datetime
from datetime import timedelta, date

import tornado.gen
from bson.objectid import ObjectId

import usosinstances
from staracommon import constants
from staracommon.helpers import log_execution_time
from staracommon.mongo_dao import Dao
from staracommon.usosutils.usosasync import UsosAsync
from staracommon.usosutils.usosclient import UsosClient


class UsosCrowler:
    def __init__(self, dao=None):
        if not dao:
            self.dao = Dao()
        else:
            self.dao = dao

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
            logging.info(
                'recreating dictionaries in collections {0} for {1}'.format(
                    constants.COLLECTION_COURSES_CLASSTYPES,
                    usos[constants.USOS_ID]))
            inserts = []
            class_types = yield self.usosAsync.get_courses_classtypes(usos[constants.USOS_URL])
            if len(class_types) > 0:
                for class_type in class_types.values():
                    class_type[constants.USOS_ID] = usos[constants.USOS_ID]
                    class_type[constants.CREATED_TIME] = recreate_time
                    class_type[constants.UPDATE_TIME] = recreate_time
                    inserts.append(class_type)
                self.dao.insert(constants.COLLECTION_COURSES_CLASSTYPES, inserts)
                logging.debug(
                    "dictionary course classtypes for usos {0} inserted.".format(usos[constants.USOS_ID]))
            else:
                raise Exception(
                    'fail to recreate_dictionaries {0} for {1}'.format(constants.COLLECTION_COURSES_CLASSTYPES,
                                                                       usos[constants.USOS_ID]))
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
                self.dao.insert(constants.COLLECTION_USOSINSTANCES, usos)

    def __build_user_info(self, client, user_id, user_info_id, crowl_time, usos):

        result = client.user_info(user_info_id)
        result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
        if user_id:
            result[constants.USER_ID] = user_id
        ui_doc = self.dao.insert(constants.COLLECTION_USERS_INFO, result)
        logging.debug('user_info inserted: {0}'.format(ui_doc))

        # if user has photo - download
        if 'has_photo' in result and result['has_photo']:
            if not self.dao.get_users_info_photo(result[constants.USER_INFO_ID], usos[constants.USOS_ID]):
                photo = client.user_info_photo(result[constants.USER_INFO_ID])
                if photo:
                    photo = self.append(photo, usos[constants.USOS_ID], crowl_time, crowl_time)
                    photo_doc = self.dao.insert(constants.COLLECTION_PHOTOS, photo)
                    logging.debug('photo for user_id: {0} inserted {1}'.format(photo[constants.USER_ID], photo_doc))
                else:
                    logging.debug('no photo for user_id: {0}'.format(user_id))

        # if users conducts some curses - fetch courses
        if result['course_editions_conducted']:
            for courseterm in result['course_editions_conducted']:
                course_id, term_id = courseterm['id'].split('|')
                course_doc = self.dao.get_course_edition(course_id, term_id, usos[constants.USOS_ID])
                if course_doc:
                    continue
                else:
                    course_result = client.course_edition(course_id, term_id, fetch_participants=False)
                    course_result = self.append(course_result, usos[constants.USOS_ID], crowl_time, crowl_time)
                    course_doc = self.dao.insert(constants.COLLECTION_COURSE_EDITION, course_result)
                    logging.debug(
                        "course_edition for course_id: {0} term_id: {1} inserted: {2}".format(course_id, term_id,
                                                                                              course_doc))

    def __build_tt(self, client, user_id, crowl_time, usos, given_date):

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
            result = client.tt(given_date)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                result[constants.USER_ID] = user_id
                tt_doc = self.dao.insert(constants.COLLECTION_TT, result)
                logging.debug('time tables for date: {0} inserted: {1}'.format(given_date, tt_doc))
            else:
                logging.debug('no time tables for date: {0}'.format(given_date))

    def __build_programmes(self, client, user_id, crowl_time, usos):

        programmes = self.dao.get_user_programmes(usos[constants.USOS_ID])
        for programme in programmes:
            result = client.programme(programme['programme']['id'])
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                result[constants.PROGRAMME_ID] = result.pop('id')
                prog_doc = self.dao.insert(constants.COLLECTION_PROGRAMMES, result)
                logging.debug('programme {0} inserted: {1}'.format(programme['id'], prog_doc))
            else:
                logging.debug('no programme: {0}.'.format(programme['id']))

    def __build_curseseditions(self, client, crowl_time, user_id, usos):

        result = client.courseeditions_info()
        if result:
            result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
            result[constants.USER_ID] = user_id
            ce_doc = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
            logging.debug('course_editions for user_id: {0} inserted: {1}'.format(user_id, ce_doc))
        else:
            logging.debug('no course_editions for user_id: {0}'.format(user_id))

    @tornado.gen.coroutine
    def __build_terms(self, user_id, usos, crowl_time):

        for term_id in self.dao.get_user_terms(user_id):

            if self.dao.get_term(term_id, usos[constants.USOS_ID]):
                continue  # term already exists
            result = yield self.usosAsync.get_term_info(usos[constants.USOS_URL], term_id)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                t_doc = self.dao.insert(constants.COLLECTION_TERMS, result)
                logging.debug('terms for term_id: {0} inserted {1}'.format(term_id, t_doc))
            else:
                logging.debug('no terms for term_id: {0}.'.format(term_id))

    @tornado.gen.coroutine
    def __build_course_edition(self, client, user_id, usos, crowl_time):

        for course_edition in self.dao.get_user_courses(user_id, usos[constants.USOS_ID]):
            if self.dao.get_course(course_edition[constants.COURSE_ID], usos[constants.USOS_ID]):
                continue  # course already exists

            result = client.course_edition(course_edition[constants.COURSE_ID], course_edition[constants.TERM_ID],
                                           fetch_participants=True)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                c_doc = self.dao.insert(constants.COLLECTION_COURSE_EDITION, result)
                logging.debug('course_edition for course_id: {0} term_id: {1} inserted {2}'.format(course_edition[
                                                                                                       constants.COURSE_ID],
                                                                                                   course_edition[
                                                                                                       constants.TERM_ID],
                                                                                                   c_doc))
            else:
                logging.debug('no course_edition for course_id: {0} term_id: {1}.'.format(course_edition[
                                                                                              constants.COURSE_ID],
                                                                                          course_edition[
                                                                                              constants.TERM_ID]))

    @tornado.gen.coroutine
    def __build_courses(self, client, usos, crowl_time):

        for course_edition in self.dao.get_course_edition_all(usos[constants.USOS_ID]):
            if self.dao.get_course(course_edition[constants.COURSE_ID], usos[constants.USOS_ID]):
                continue  # course already exists

            result = client.course(course_edition[constants.COURSE_ID])
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                result[constants.COURSE_ID] = result.pop('id')
                c_doc = self.dao.insert(constants.COLLECTION_COURSES, result)
                logging.debug(
                    'course for course_id: {0} inserted {1}'.format(course_edition[constants.COURSE_ID], c_doc))
            else:
                logging.debug('no course for course_id: {0}.'.format(course_edition[constants.COURSE_ID]))

    @tornado.gen.coroutine
    def __build_faculties(self, client, usos, crowl_time):
        for faculty in self.dao.get_faculties_from_courses(usos[constants.USOS_ID]):
            if self.dao.get_faculty(faculty, usos[constants.USOS_ID]):
                continue  # fac already exists

            result = client.faculty(faculty)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                result[constants.FACULTY_ID] = faculty
                fac_doc = self.dao.insert(constants.COLLECTION_FACULTIES, result)
                logging.debug('faculty for fac_id: {0} inserted {1}'.format(faculty, fac_doc))
            else:
                logging.debug('no faculty for fac_id: {0}.'.format(faculty))

    @tornado.gen.coroutine
    def __build_user_infos(self, client, crowl_time, users, usos):
        for user in users:
            if not self.dao.get_users_info_by_usos_id(user['id'], usos):
                self.__build_user_info(client, None, user['id'], crowl_time, usos)
                logging.debug('Fetched user_info for user with id: {0}'.format(user['id']))

    @tornado.gen.coroutine
    def __build_units(self, client, crowl_time, units, usos):

        for unit_id in units:
            if self.dao.get_units(unit_id, usos[constants.USOS_ID]):
                continue  # units already exists

            result = client.units(unit_id)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                result[constants.UNIT_ID] = result.pop('id')
                u_doc = self.dao.insert(constants.COLLECTION_COURSES_UNITS, result)
                logging.debug('unit {0} inserted {1}'.format(unit_id, u_doc))
            else:
                logging.debug('no unit {0}.'.format(unit_id))

    @tornado.gen.coroutine
    def __build_groups(self, client, crowl_time, units, usos):

        for unit in units:
            result = client.groups(unit)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
                grp_doc = self.dao.insert(constants.COLLECTION_GROUPS, result)
                logging.debug('group for unit: {0} inserted: {1}'.format(unit, grp_doc))
            else:
                logging.debug('no group for unit: {0}'.format(unit))

    @tornado.gen.coroutine
    def __build_grades_participants_lecturers_units_groups(self, client, user_id, usos, crowl_time):

        all_participants = []
        all_lecturers = []
        all_units = []
        for data in self.dao.get_user_courses_editions(user_id):
            term_id, course_id = data[0], data[1]

            # participants ane lectures
            result = client.course_edition(course_id, term_id, fetch_participants=True)
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
                result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
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
                    "grades for course_id: {0} and term_id: {1} inserted {2}".format(course_id, term_id, g_doc))

        self.__build_user_infos(client, crowl_time, all_participants, usos)
        self.__build_user_infos(client, crowl_time, all_lecturers, usos)

        self.__build_units(client, crowl_time, all_units, usos)
        self.__build_groups(client, crowl_time, all_units, usos)

    @log_execution_time
    @tornado.gen.coroutine
    def initial_user_crowl(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        crowl_time = datetime.now()

        user = self.dao.get_user(user_id)
        if not user:
            logging.error("could not crowl for usos data for unknown user with id: {0}".format(user_id))
            return

        usos = self.dao.get_usos(user[constants.USOS_ID])

        client = UsosClient(usos[constants.USOS_URL], usos[constants.CONSUMER_KEY],
                            usos[constants.CONSUMER_SECRET],
                            user[constants.ACCESS_TOKEN_KEY], user[constants.ACCESS_TOKEN_SECRET])
        try:
            self.__build_user_info(client, user_id, None, crowl_time, usos)

            # fetch tt for current and next week
            today = date.today()
            next_week = today + timedelta(days=constants.TIME_TABLE_DELTA)

            self.__build_tt(client, user_id, crowl_time, usos, today)
            self.__build_tt(client, user_id, crowl_time, usos, next_week)

            self.__build_programmes(client, user_id, crowl_time, usos)

            self.__build_curseseditions(client, crowl_time, user_id, usos)

            yield self.__build_terms(user_id, usos, crowl_time)

            self.__build_course_edition(client, user_id, usos, crowl_time)

            yield self.__build_grades_participants_lecturers_units_groups(client, user_id, usos, crowl_time)

            self.__build_courses(client, usos, crowl_time)

            self.__build_faculties(client, usos, crowl_time)

            # crowl collection
            result = self.append(dict(), usos[constants.USOS_ID], crowl_time, crowl_time)
            result[constants.USER_ID] = user_id
            doc = self.dao.insert(constants.COLLECTION_CROWLLOG, result)
            logging.info('crowl log inserted with id {0}'.format(doc))

        except Exception, ex:
            logging.exception("Exception while initial user usos crowler")
