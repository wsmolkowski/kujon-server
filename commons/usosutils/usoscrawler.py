import logging
from datetime import datetime
from datetime import timedelta, date
import tornado.gen
from bson.objectid import ObjectId
import usosinstances
from commons import constants
from commons.AESCipher import AESCipher
from commons.helpers import log_execution_time
from commons.mongo_dao import Dao
from commons.usosutils.usosasync import UsosAsync
from commons.usosutils.usosclient import UsosClient

log = logging.getLogger(__name__)


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
            logging.info("recreating dictionaries in collections %r for %r", constants.COLLECTION_COURSES_CLASSTYPES,
                usos[constants.USOS_ID])
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
                    "dictionary course classtypes for usos %r inserted.", usos[constants.USOS_ID])
            else:
                raise Exception("fail to recreate_dictionaries %r for %r", constants.COLLECTION_COURSES_CLASSTYPES, usos[constants.USOS_ID])
        raise tornado.gen.Return(True)

    def drop_collections(self):
        self.dao.drop_collections()

    @log_execution_time
    def recreate_usos(self):
        self.dao.drop_collection(constants.COLLECTION_USOSINSTANCES)
        for usos in usosinstances.USOSINSTANCES:
            logging.info("adding usos: %r ", usos[constants.USOS_ID])
            doc = self.dao.find_usos(usos[constants.USOS_ID])
            if not doc:
                self.dao.insert(constants.COLLECTION_USOSINSTANCES, self.aes.encrypt_usos(usos))

    def __build_user_info_photo(self, client, user_id, user_info_id, crawl_time, usos):
        if not self.dao.get_users_info_photo(user_info_id, usos[constants.USOS_ID]):
            photo = client.user_info_photo(user_info_id)
            if photo:
                photo = self.append(photo, usos[constants.USOS_ID], crawl_time, crawl_time)
                photo_doc = self.dao.insert(constants.COLLECTION_PHOTOS, photo)
                logging.debug("photo for user_id: %r inserted %r", photo[constants.USER_ID], str(photo_doc))
                return photo_doc
            else:
                logging.debug("no photo for user_id: %r", user_id)

    def __build_user_info(self, client, user_id, user_info_id, crawl_time, usos):
        if user_id and self.dao.user_info_exists(user_id):
            logging.debug("not building user info - it already exists for %r", user_id)
            return

        result = client.user_info(user_info_id)
        result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
        if user_id:
            result[constants.USER_ID] = user_id

        # if user has photo - download
        if 'has_photo' in result and result['has_photo']:
            result['has_photo'] = self.__build_user_info_photo(client, user_id, result[constants.ID],
                                                               crawl_time, usos)

        # strip english values and if value is empty change to None
        result['office_hours'] = result['interests']['pl']
        result['interests'] = result['interests']['pl']

        # strip empty values
        if result['homepage_url'] and result['homepage_url'] == "":
            result['homepage_url'] = None

        # strip english names from programmes description
        for programme in result['student_programmes']:
            programme['programme']['description'] = programme['programme']['description']['pl']

        ui_doc = self.dao.insert(constants.COLLECTION_USERS_INFO, result)
        logging.debug("user_info for %r inserted: %r", result[constants.ID], str(ui_doc))

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
            
            course_result = client.course_edition(course_id, term_id, fetch_participants=False)
            course_result = self.append(course_result, usos[constants.USOS_ID], crawl_time, crawl_time)
            course_doc = self.dao.insert(constants.COLLECTION_COURSE_EDITION, course_result)
            logging.debug("course_edition for course_id: %r term_id: %r inserted: %r", course_id, term_id, str(course_doc))

    def __build_time_table(self, client, user_id, usos_id, given_date):
        existing_tt = self.dao.get_time_table(user_id, usos_id)
        try:
            result = client.time_table(given_date)
        except Exception, ex:
            logging.exception('Exception {0} while fetching time table for: {1} and {2}'.format(
                ex.message, user_id, given_date))
            return

        if result:
            tt = dict()
            tt[constants.USOS_ID] = usos_id
            tt[constants.TT_STARTDATE] = str(given_date)
            tt['tts'] = result
            tt[constants.USER_ID] = user_id
            tt_doc = self.dao.insert(constants.COLLECTION_TT, tt)
            logging.debug("time tables for date: %r inserted: %r", given_date, tt_doc)

            # if existing_tt:
            #     self.dao.remove(constants.COLLECTION_TT, existing_tt)
        else:
            logging.debug("no time tables for date: %r inserted empty", given_date)

    def __build_programmes(self, client, user_info_id, crawl_time, usos):

        for programme in self.dao.get_users_info_programmes(user_info_id, usos[constants.USOS_ID]):
            # checking if program exists in mongo
            if self.dao.get_programme(programme['programme'][constants.ID], usos[constants.USOS_ID]):
                continue
            
            result = client.programme(programme['programme'][constants.ID])
            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.PROGRAMME_ID] = result.pop(constants.ID)

                # strip english names
                result['name'] = result['name']['pl']
                result['mode_of_studies'] = result['mode_of_studies']['pl']
                result['level_of_studies'] = result['level_of_studies']['pl']
                result['duration'] = result['duration']['pl']
                result['description'] = result['description']['pl']

                prog_doc = self.dao.insert(constants.COLLECTION_PROGRAMMES, result)
                logging.debug("programme %r inserted: %r.", programme[constants.ID], str(prog_doc))
            else:
                logging.debug("no programme: %r.", programme[constants.ID])

    def __build_curseseditions(self, client, crawl_time, user_id, usos):
        if self.dao.curseseditions_id(user_id):
            logging.debug("courses_editions exists for user_id: %r", user_id)
            return

        result = client.courseeditions_info()
        if result:
            result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
            result[constants.USER_ID] = user_id
            ce_doc = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
            logging.debug("course_editions for user_id: %r inserted: %r", user_id, str(ce_doc))
        else:
            logging.debug("no course_editions for user_id: %r", user_id)

    def __update_curseseditions(self, client, crawl_time, user_id, usos):

        existing_id = self.dao.curseseditions_id(user_id)

        result = client.courseeditions_info()
        result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
        result[constants.USER_ID] = user_id

        ce_doc = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
        logging.debug("course_editions for user_id: %r inserted: %r", str(user_id), str(ce_doc))

        if existing_id and ce_doc:
            self.dao.delete_doc(constants.COLLECTION_COURSES_EDITIONS, existing_id)

    @tornado.gen.coroutine
    def __build_terms(self, user_id, usos, crawl_time):

        for term_id in self.dao.get_user_terms(user_id):

            if self.dao.get_term(term_id, usos[constants.USOS_ID]):
                continue  # term already exists

            result = yield self.usosAsync.get_term_info(usos[constants.USOS_URL], term_id)
            result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
            t_doc = self.dao.insert(constants.COLLECTION_TERMS, result)
            logging.debug("terms for term_id: %r inserted %r", term_id, str(t_doc))

    @tornado.gen.coroutine
    def __build_course_edition(self, client, user_id, usos, crawl_time):

        for course_edition in self.dao.get_user_courses(user_id, usos[constants.USOS_ID]):
            existing_doc = self.dao.get_course_edition(course_edition[constants.COURSE_ID],
                                                       course_edition[constants.TERM_ID], usos[constants.USOS_ID])

            result = client.course_edition(course_edition[constants.COURSE_ID], course_edition[constants.TERM_ID],
                                           fetch_participants=True)

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                c_doc = self.dao.insert(constants.COLLECTION_COURSE_EDITION, result)
                logging.debug("course_edition for course_id: %r term_id: %r inserted %r", course_edition[
                                                    constants.COURSE_ID], course_edition[constants.TERM_ID], str(c_doc))

                if existing_doc:
                    self.dao.delete_doc(constants.COLLECTION_COURSE_EDITION, existing_doc[constants.MONGO_ID])
            else:
                logging.debug("no course_edition for course_id: %r term_id: %r", course_edition[
                                                        constants.COURSE_ID], course_edition[constants.TERM_ID])

    @tornado.gen.coroutine
    def __build_courses(self, client, user_id, usos, crawl_time):

        courses = list()
        for course_edition in self.dao.get_courses_editions(user_id, usos[constants.USOS_ID]):
            for term in course_edition['course_editions']:
                for course in course_edition['course_editions'][term]:
                    courses.append(course[constants.COURSE_ID])

        # get courses conducted by lecturers
        for course_conducted in self.dao.get_courses_conducted_by_lecturers(usos[constants.USOS_ID]):
            if len(course_conducted['course_editions_conducted']) > 0:
                for courseedition in course_conducted['course_editions_conducted']:
                    course_id, term_id = courseedition['id'].split('|')
                    courses.append(course_id)

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
                    result[constants.COURSE_ID] = result.pop(constants.ID)

                    # strip english names
                    result['name'] = result['name']['pl']
                    result['learning_outcomes'] = result['learning_outcomes']['pl']
                    result['description'] = result['description']['pl']
                    result['assessment_criteria'] = result['assessment_criteria']['pl']
                    result['bibliography'] = result['bibliography']['pl']

                    c_doc = self.dao.insert(constants.COLLECTION_COURSES, result)

                    logging.debug("course for course_id: %r inserted %r", course, str(c_doc))
                else:
                    logging.debug("no course for course_id: %r.", course)

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
                logging.debug("faculty for fac_id: %r inserted %r", faculty, str(fac_doc))
            else:
                logging.debug("no faculty for fac_id: %r.", faculty)

    @tornado.gen.coroutine
    def __build_users_info(self, client, crawl_time, users, usos):
        for user in users:
            if not self.dao.get_users_info(user[constants.ID], usos):
                # build user_info
                self.__build_user_info(client, None, user[constants.ID], crawl_time, usos)

                # build programme for given user
                self.__build_programmes(client, user[constants.ID], crawl_time, usos)

    @tornado.gen.coroutine
    def __build_units(self, client, crawl_time, units, usos):

        for unit_id in units:
            if self.dao.get_units(unit_id, usos[constants.USOS_ID]):
                continue  # units already exists

            result = client.units(unit_id)
            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.UNIT_ID] = result.pop(constants.ID)
                u_doc = self.dao.insert(constants.COLLECTION_COURSES_UNITS, result)
                logging.debug("unit %r inserted %r.", unit_id, str(u_doc))
            else:
                logging.debug("no unit %r.", format(unit_id))

    @tornado.gen.coroutine
    def __build_groups(self, client, crawl_time, units, usos):

        for unit in units:
            result = client.groups(unit)

            if result:
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                grp_doc = self.dao.insert(constants.COLLECTION_GROUPS, result)
                logging.debug("group for unit: %r inserted: %r", unit, str(grp_doc))
            else:
                logging.debug("no group for unit: %r.", unit)

    @tornado.gen.coroutine
    def __process_user_data(self, client, user_id, usos, crawl_time):

        users_found = list()
        units_found = list()

        for data in self.dao.get_user_courses_editions(user_id):
            term_id, course_id = data[0], data[1]
            result = client.course_edition(course_id, term_id, fetch_participants=True)

            self.__find_users_related(users_found, result)

            # units
            if result and 'course_units_ids' in result:
                for unit in result['course_units_ids']:
                    if unit not in units_found:
                        units_found.append(unit)

                units = result['course_units_ids']
                result = self.append(result, usos[constants.USOS_ID], crawl_time, crawl_time)
                result[constants.USER_ID] = user_id
                if self.dao.get_grades(course_id, term_id, user_id, usos[constants.USOS_ID]):
                    continue  # grades for course and term already exists

            if result:
                g_doc = self.dao.insert(constants.COLLECTION_GRADES, result)
                logging.debug("grades for course_id: %r and term_id: %r inserted %r", course_id, term_id, str(g_doc))

        self.__build_users_info(client, crawl_time, users_found, usos)
        self.__build_units(client, crawl_time, units_found, usos)
        self.__build_groups(client, crawl_time, units_found, usos)

    @staticmethod
    def __find_users_related(users, result):
        if result and 'participants' in result:
            participants = result.pop('participants')
            lecturers = result.pop('lecturers')
            for p in participants:
                if p not in users:
                    users.append(p)
            for l in lecturers:
                if l not in users:
                    users.append(l)

    def __build_client(self, user):
        usos = self.dao.get_usos(user[constants.USOS_ID])
        client = UsosClient(usos[constants.USOS_URL], usos[constants.CONSUMER_KEY],
                            usos[constants.CONSUMER_SECRET],
                            user[constants.ACCESS_TOKEN_KEY], user[constants.ACCESS_TOKEN_SECRET])
        return client, usos

    @log_execution_time
    @tornado.gen.coroutine
    def initial_user_crawl(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        crawl_time = datetime.now()

        user = self.dao.get_user(user_id)
        if not user:
            raise Exception("Initial crawler not started. Unknown user with id: %r.", user_id)

        client, usos = self.__build_client(user)

        user_info_id = self.__build_user_info(client, user_id, None, crawl_time, usos)

        # fetch time_table for current and next week
        monday = self.__get_monday()
        self.__build_time_table(client, user_id, usos[constants.USOS_ID], monday)
        self.__build_time_table(client, user_id, usos[constants.USOS_ID], self.__get_next_monday(monday))

        self.__build_programmes(client, user_info_id, crawl_time, usos)

        self.__build_curseseditions(client, crawl_time, user_id, usos)

        yield self.__build_terms(user_id, usos, crawl_time)

        self.__build_course_edition(client, user_id, usos, crawl_time)

        yield self.__process_user_data(client, user_id, usos, crawl_time)

        self.__build_courses(client, user_id, usos, crawl_time)

        self.__build_faculties(client, usos, crawl_time)

    @staticmethod
    def __get_next_monday(monday):
        return monday + timedelta(days=7)

    @staticmethod
    def __get_monday():
        today = date.today()
        monday = today - timedelta(days=(today.weekday()) % 7)
        return monday

    @log_execution_time
    @tornado.gen.coroutine
    def update_user_crawl(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        crawl_time = datetime.now()

        user = self.dao.get_user(user_id)
        if not user:
            raise Exception("Update crawler not started. Unknown user with id: %r", user_id)

        client, usos = self.__build_client(user)

        courses_conducted = self.dao.courses_conducted(user_id)

        self.__build_course_editions_for_conducted(client, courses_conducted, crawl_time, usos)

        #user_info_id = self.dao.user_info_id(user_id)

        self.__build_faculties(client, usos, crawl_time)

    @tornado.gen.coroutine
    def update_time_tables(self):
        monday = self.__get_monday()
        next_monday = self.__get_next_monday(monday)

        for user in self.dao.get_users():
            try:
                logging.debug('updating time table for user: {0} and monday: {1}'.format(user[constants.MONGO_ID], monday))
                client, usos = self.__build_client(user)

                self.__build_time_table(client, user[constants.MONGO_ID], user[constants.USOS_ID], monday)
                self.__build_time_table(client, user[constants.MONGO_ID], user[constants.USOS_ID], next_monday)

                logging.debug('updating time table for user: {0}'.format(user[constants.MONGO_ID]))
            except Exception, ex:
                logging.exception('Exception in update_time_tables {0}'.format(ex.message))


