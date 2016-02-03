import json
import logging
from datetime import datetime

import tornado.gen

import usosapi.constants
import usoshelper
import usosinstances
from usosapi.mongo_dao import Dao
from usosupdater import USOSUpdater


class UsosCrowler():
    def __init__(self, dao=None):
        if not dao:
            self.dao = Dao()
        else:
            self.dao = dao

    def __update_dict(self, data, user_id, usos, create_time, update_time):
        if not data:
            data = dict()

        if not user_id:
            data[usosapi.constants.USER_ID] = user_id

        if not usos:
            data[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]

        if not create_time:
            data[usosapi.constants.CREATED_TIME] = create_time

        if not update_time:
            data[usosapi.constants.UPDATE_TIME] = update_time

        return data

    @tornado.gen.coroutine
    def recreate_dictionaries(self):

        recreate_time = datetime.now()

        self.dao.drop_collection(usosapi.constants.COLLECTION_COURSES_CLASSTYPES)
        for usos in self.dao.get_usoses():
            logging.info(
                'recreating dictionaries in collections {0} for {1}'.format(
                    usosapi.constants.COLLECTION_COURSES_CLASSTYPES,
                    usos[usosapi.constants.USOS_ID]))
            inserts = []
            class_types = yield usoshelper.get_courses_classtypes(usos[usosapi.constants.URL])
            if len(class_types) > 0:
                for class_type in class_types.values():
                    class_type[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
                    class_type[usosapi.constants.CREATED_TIME] = recreate_time
                    class_type[usosapi.constants.UPDATE_TIME] = recreate_time
                    inserts.append(class_type)
                doc = self.dao.insert(usosapi.constants.COLLECTION_COURSES_CLASSTYPES, inserts)
            else:
                raise Exception(
                    'fail to recreate_dictionaries {0} for {1}'.format(usosapi.constants.COLLECTION_COURSES_CLASSTYPES,
                                                                       usos[usosapi.constants.USOS_ID]))
        raise tornado.gen.Return(True)

    def drop_collections(self):
        self.dao.drop_collections()

    def recreate_usos(self):
        self.dao.drop_collection(usosapi.constants.COLLECTION_USOSINSTANCES)
        for usos in usosinstances.USOSINSTANCES:
            logging.info('adding usos: {0} '.format(usos[usosapi.constants.USOS_ID]))
            doc = self.dao.find_usos(usos[usosapi.constants.USOS_ID])
            if not doc:
                self.dao.insert(usosapi.constants.COLLECTION_USOSINSTANCES, usos)

    @tornado.gen.coroutine
    def initial_user_crowl(self, user_id):
        logging.debug('crawling for user id: {0}'.format(user_id))
        crowl_time = datetime.now()

        user = self.dao.get_user(user_id)
        if not user:
            logging.error("could not crowl for usos data for unknown user with id: {0}".format(user_id))
            return

        usos = self.dao.get_usos(user[usosapi.constants.USOS_ID])

        updater = USOSUpdater(usos[usosapi.constants.URL], usos[usosapi.constants.CONSUMER_KEY],
                              usos[usosapi.constants.CONSUMER_SECRET],
                              user[usosapi.constants.ACCESS_TOKEN_KEY], user[usosapi.constants.ACCESS_TOKEN_SECRET])

        # user_info
        user_info = self.dao.get_users_info(user_id)
        if not user_info:
            result = updater.request_user_info()
            result[usosapi.constants.USER_ID] = user_id
            result[usosapi.constants.CREATED_TIME] = crowl_time
            doc = self.dao.insert(usosapi.constants.COLLECTION_USERS_INFO, result)
            logging.debug('user_info for user_id {0} inserted: {1}'.format(user_id, doc))
        else:
            result = updater.request_user_info()
            result[usosapi.constants.UPDATE_TIME] = crowl_time
            result[usosapi.constants.USER_ID] = user_id
            result = self.dao.update(usosapi.constants.COLLECTION_USERS_INFO, usosapi.constants.ID, user_info[
                usosapi.constants.ID], result)
            logging.debug('user_info updated: {0}'.format(user_info[usosapi.constants.ID]))

        # course_editions
        courseseditions = self.dao.get_courses_editions(user_id)
        if not courseseditions:
            result = updater.request_courses_editions()
            result[usosapi.constants.UPDATE_TIME] = crowl_time
            result[usosapi.constants.USER_ID] = user_id
            result[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
            courseseditions = self.dao.insert(usosapi.constants.COLLECTION_COURSES_EDITIONS, result)
            logging.debug('course_editions inserted into courses_editions: {0}'.format(courseseditions))
        else:
            result = updater.request_courses_editions()
            result[usosapi.constants.UPDATE_TIME] = crowl_time
            result[usosapi.constants.USER_ID] = user_id
            result = self.dao.update(usosapi.constants.COLLECTION_COURSES_EDITIONS, usosapi.constants.ID, courseseditions[
                usosapi.constants.ID],
                                     result)
            logging.debug('course_editions updated: {0}'.format(courseseditions[usosapi.constants.ID]))

        # terms
        for term_id in self.dao.get_user_terms(user_id):

            term = self.dao.get_terms(term_id, user_id)
            result = yield usoshelper.get_term_info(usos[usosapi.constants.URL], term_id)
            result = json.loads(result)
            result[usosapi.constants.USER_ID] = user_id
            result[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
            if not term:
                result[usosapi.constants.CREATED_TIME] = crowl_time
            else:
                result[usosapi.constants.CREATED_TIME] = term[usosapi.constants.CREATED_TIME]
                self.dao.remove(usosapi.constants.COLLECTION_TERMS, usosapi.constants.ID, term[usosapi.constants.ID])
            result[usosapi.constants.UPDATE_TIME] = crowl_time
            result[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
            doc = self.dao.insert(usosapi.constants.COLLECTION_TERMS, result)
            if not term:
                logging.debug('term with term_id: {0} inserted with id: {1}'.format(term_id, doc))
            else:
                logging.debug('term with term_id: {0} updated with new id: {1}'.format(term_id, doc))

        # courses
        for course_id in self.dao.get_user_courses(user_id):
            course = self.dao.get_courses(course_id, user_id)
            result = yield usoshelper.get_course_info(usos[usosapi.constants.URL], course_id)
            result = json.loads(result)
            result[usosapi.constants.USER_ID] = user_id
            result[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
            if not course:
                result[usosapi.constants.CREATED_TIME] = crowl_time
            else:
                result[usosapi.constants.CREATED_TIME] = course[usosapi.constants.CREATED_TIME]
                self.dao.remove(usosapi.constants.COLLECTION_TERMS, usosapi.constants.ID, term[usosapi.constants.ID])
            result[usosapi.constants.UPDATE_TIME] = crowl_time
            doc = self.dao.insert(usosapi.constants.COLLECTION_COURSES, result)
            if not course:
                logging.debug('course with course_id: {0} inserted with id: {1}'.format(course_id, doc))
            else:
                logging.debug('course with course_id: {0} updated with new id: {1} '.format(course_id, doc))

        # grades and participants and units
        for data in self.dao.get_user_courses_editions(user_id):
            term_id, course_id = str(data[0]), str(data[1])
            grades = self.dao.get_grades(course_id, term_id, user_id)
            result = updater.request_grades_for_course(course_id, term_id)
            participants = result.pop('participants')
            units = result.pop('course_units_ids')
            result[usosapi.constants.USER_ID] = user_id
            result[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
            if not grades:
                result[usosapi.constants.CREATED_TIME] = crowl_time
            else:
                result[usosapi.constants.CREATED_TIME] = grades[usosapi.constants.CREATED_TIME]
                self.dao.remove(usosapi.constants.COLLECTION_GRADES, usosapi.constants.ID, grades[usosapi.constants.ID])
            result[usosapi.constants.UPDATE_TIME] = crowl_time
            doc = self.dao.insert(usosapi.constants.COLLECTION_GRADES, result)
            if not grades:
                logging.info(
                    'grades for term_id: {0} and course_id: {1} inserted with id: {2} '.format(term_id, course_id, doc))
            else:
                logging.info(
                    'grades for term_id: {0} and course_id: {1} updated with id: {2} '.format(term_id, course_id, doc))

            # participants
            result = dict()
            participants = self.dao.get_participants(course_id, term_id)
            result[usosapi.constants.TERM_ID] = term_id
            result[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
            result[usosapi.constants.COURSE_ID] = course_id
            result[usosapi.constants.PARTICIPANTS] = participants
            if not participants:
                result[usosapi.constants.CREATED_TIME] = crowl_time
            else:
                result[usosapi.constants.CREATED_TIME] = participants[usosapi.constants.CREATED_TIME]
                self.dao.remove(usosapi.constants.COLLECTION_PARTICIPANTS, term_id, course_id)
            result[usosapi.constants.UPDATE_TIME] = crowl_time
            doc = self.dao.insert(usosapi.constants.COLLECTION_PARTICIPANTS, result)
            if not participants:
                logging.debug(
                    'participants for term_id: {0} and course_id: {1} inserted with id: {2}'.format(term_id, course_id,
                                                                                                    doc))
            else:
                logging.debug(
                    'participants for term_id: {0} and course_id: {1} updated with id: {2}'.format(term_id, course_id,
                                                                                                   doc))
            # units
            for unit_id in units:
                unit = self.dao.get_courses_units(unit_id)
                result = yield usoshelper.get_courses_units(usos[usosapi.constants.URL], unit_id)
                result = json.loads(result)
                if not unit:
                    result[usosapi.constants.USOS_ID] = usos[usosapi.constants.USOS_ID]
                    result[usosapi.constants.CREATED_TIME] = crowl_time
                else:
                    result[usosapi.constants.CREATED_TIME] = unit[usosapi.constants.CREATED_TIME]
                    self.dao.remove(usosapi.constants.COLLECTION_COURSES_UNITS, usosapi.constants.UNIT_ID, unit)
                doc = self.dao.insert(usosapi.constants.COLLECTION_COURSES_UNITS, result)
                if not unit:
                    logging.debug('unit {0} inserted with id: {1}'.format(unit_id, doc))
                else:
                    logging.debug('unit {0} updated for id: {1}'.format(unit_id, doc))

        # crowl collection
        result = dict()
        result[usosapi.constants.USER_ID] = user_id
        result[usosapi.constants.CREATED_TIME] = crowl_time
        result[usosapi.constants.UPDATE_TIME] = datetime.now()

        doc = self.dao.insert(usosapi.constants.COLLECTION_CROWLLOG, result)
        logging.debug('crowl log inserted with id {0}'.format(doc))
