import logging
from datetime import datetime

import tornado.gen
from bson.objectid import ObjectId

import usosasync
import usosinstances
from usosapi import constants
from usosapi.helpers import log_execution_time
from usosapi.mongo_dao import Dao
from usosapi.usosutils.usosclient import UsosClient


class UsosCrowler:
    def __init__(self, dao=None):
        if not dao:
            self.dao = Dao()
        else:
            self.dao = dao

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
            class_types = yield usosasync.get_courses_classtypes(usos[constants.USOS_URL])
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
        '''
            fetches user info and inserts to database
        :param client:
        :param user_id:
        :param crowl_time:
        :return:
        '''
        result = client.user_info(user_info_id)
        result = self.append(result, None, crowl_time, crowl_time)
        if user_id:
            result[constants.USER_ID] = user_id
        result[constants.USOS_ID] = usos[constants.USOS_ID]
        ui_doc = self.dao.insert(constants.COLLECTION_USERS_INFO, result)
        logging.debug('user_info inserted: {0}'.format(ui_doc))

    def __build_programmes(self, client, user_id, crowl_time, usos):

        programmes = self.dao.get_user_programmes(user_id)
        for prog in programmes:
            result = client.programme(prog['programme']['id'])
            result = self.append(result, None, crowl_time, crowl_time)
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            result[constants.PROGRAMME_ID] = result.pop('id')

            prog_doc = self.dao.insert(constants.COLLECTION_PROGRAMMES, result)
            logging.debug('programme for prog: {0} inserted: {1}'.format(prog['id'], prog_doc))

    def __build_curseseditions(self, client, crowl_time, user_id, usos):
        '''
            fetches curseseditions and inserts to database
        :param client:
        :param crowl_time:
        :param user_id:
        :param usos:
        :return:
        '''
        result = client.courseeditions_info()
        result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
        result[constants.USER_ID] = user_id
        ce_doc = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
        logging.debug('course_editions for user_id: {0} inserted: {1}'.format(user_id, ce_doc))

    @tornado.gen.coroutine
    def __build_terms(self, client, user_id, usos, crowl_time):
        '''
            for each user unique term fetches usos data and inserts to database if not exists
        :param user_id:
        :param usos:
        :param crowl_time:
        :return:
        '''
        for term_id in self.dao.get_user_terms(user_id):

            if self.dao.get_term(term_id, usos[constants.USOS_ID]):
                continue  # term already exists
            result = yield usosasync.get_term_info(usos[constants.USOS_URL], term_id)

            result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
            t_doc = self.dao.insert(constants.COLLECTION_TERMS, result)
            logging.debug('terms for term_id: {0} inserted {1}'.format(term_id, t_doc))

    @tornado.gen.coroutine
    def __build_courses(self, client, user_id, usos, crowl_time):
        '''
            for each user unique course fetches usos data and inserts to database if not exists
        :param user_id:
        :param usos:
        :param crowl_time:
        :return:
        '''
        for course_id in self.dao.get_user_courses(user_id):
            if self.dao.get_course(course_id, usos[constants.USOS_ID]):
                continue  # course already exists

            result = yield usosasync.get_course_info(usos[constants.USOS_URL], course_id)
            result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)

            c_doc = self.dao.insert(constants.COLLECTION_COURSES, result)
            logging.debug('course for course_id: {0} inserted {1}'.format(course_id, c_doc))

    @tornado.gen.coroutine
    def __build_participants(self, client, course_id, participants, crowl_time, term_id, usos):
        '''
            inserts participants to database
        :param course_id:
        :param crowl_time:
        :param participants:
        :param term_id:
        :param usos:
        :return: list of participants
        '''
        result = self.dao.get_participants(course_id, term_id, usos)
        if not result:
            result = []
            result = self.append(dict(), usos[constants.USOS_ID], crowl_time, crowl_time)
            result[constants.PARTICIPANTS] = participants
            course_doc = self.dao.get_course(course_id, usos[constants.USOS_ID])
            result[constants.COURSE_ID] = course_doc[constants.ID]
            result[constants.COURSE_ID] = course_id
            result[constants.TERM_ID] = term_id
            p_doc = self.dao.insert(constants.COLLECTION_PARTICIPANTS, result)

            logging.debug('participants inserted: {0}'.format(p_doc))

        raise tornado.gen.Return(participants)

    def __build_user_infos(self, client, crowl_time, users, usos):
        '''
            build user info for participants from list
        :param client:
        :param crowl_time:
        :param users:
        :return:
        '''

        for user in users:
            if not self.dao.get_users_info_by_usos_id(user['id'], usos):
                self.__build_user_info(client, None, user['id'], crowl_time, usos)
                logging.debug('Fetched user_info for user with id: {0}'.format(user['id']))

    @tornado.gen.coroutine
    def __build_units(self, crowl_time, units, usos):
        '''
            iterates over units and if does not exists in database fetches data from usos and inserts
        :param crowl_time:
        :param units:
        :param usos:
        :return:
        '''

        for unit_id in units:
            if self.dao.get_courses_units(unit_id, usos[constants.USOS_ID]):
                continue  # units already exists

            result = yield usosasync.get_courses_units(usos[constants.USOS_URL], unit_id)
            result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)

            u_doc = self.dao.insert(constants.COLLECTION_COURSES_UNITS, result)
            logging.debug('unit {0} inserted {1}'.format(unit_id, u_doc))

    @tornado.gen.coroutine
    def __build_groups_and_add_lectures(self, client, crowl_time, units, usos):
        '''
            iterates over units and if does not exists in database fetches data from usos and inserts
        :param crowl_time:
        :param units:
        :param usos:
        :return:
        '''
        all_lecturers = []
        for unit in units:
            result = client.groups(unit)
            result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
            if 'message' in result:
                logging.debug('failed fetching group for unit: {0}'.format(unit))
                continue
            grp_doc = self.dao.insert(constants.COLLECTION_GROUPS, result)
            logging.debug('group for unit: {0} inserted: {1}'.format(unit, grp_doc))
            for lecturer in result['lecturers']:
                if lecturer not in all_lecturers:
                    all_lecturers.append(lecturer)
                    logging.debug('lecturer: {0} found.'.format(unit, lecturer))
        self.__build_user_infos(client, crowl_time, all_lecturers, usos)


    @tornado.gen.coroutine
    def __build_grades_participants_units_groups(self, client, user_id, usos, crowl_time):
        '''
            building grades and participants and units
        :param client:
        :param user_id:
        :param usos:
        :param crowl_time:
        :return:
        '''
        all_participants = []
        all_units = []
        for data in self.dao.get_user_courses_editions(user_id):
            term_id, course_id = str(data[0]), str(data[1])

            if self.dao.get_grades(course_id, term_id, user_id):
                continue  # grades for course and term already exists

            result = client.grades(course_id, term_id)
            participants = result.pop('participants')
            units = result.pop('course_units_ids')
            result = self.append(result, usos[constants.USOS_ID], crowl_time, crowl_time)
            result[constants.USER_ID] = user_id

            g_doc = self.dao.insert(constants.COLLECTION_GRADES, result)
            logging.debug('grades for term_id: {0} course_id:{1} inserted {2}'.format(term_id, course_id, g_doc))

            participants = yield self.__build_participants(client, course_id, participants, crowl_time, term_id, usos)
            for p in participants:
                if p not in all_participants:
                    all_participants.append(p)

            for unit in units:
                if unit not in all_units:
                    all_units.append(unit)

        self.__build_user_infos(client, crowl_time, all_participants, usos)
        yield self.__build_units(crowl_time, all_units, usos)
        self.__build_groups_and_add_lectures(client, crowl_time, all_units, usos)

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

            self.__build_programmes(client, user_id, crowl_time, usos)

            self.__build_curseseditions(client, crowl_time, user_id, usos)

            yield self.__build_terms(client, user_id, usos, crowl_time)

            yield self.__build_courses(client, user_id, usos, crowl_time)

            yield self.__build_grades_participants_units_groups(client, user_id, usos, crowl_time)

            # crowl collection
            result = self.append(dict(), usos[constants.USOS_ID], crowl_time, crowl_time)
            result[constants.USER_ID] = user_id
            doc = self.dao.insert(constants.COLLECTION_CROWLLOG, result)
            logging.info('crowl log inserted with id {0}'.format(doc))

        except Exception, ex:
            logging.exception("Exception while initial user usos crowler")

