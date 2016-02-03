import json
import logging
from datetime import datetime

import tornado.gen

import constants
import settings
import usoshelper
from mongo_dao import Dao
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
            data[constants.USER_ID] = user_id

        if not usos:
            data[constants.USOS_ID] = usos[constants.USOS_ID]

        if not create_time:
            data[constants.CREATED_TIME] = create_time

        if not update_time:
            data[constants.UPDATE_TIME] = update_time

        return data

    @tornado.gen.coroutine
    def recreate_dictionaries(self):
        if settings.UPDATE_DICTIONARIES:
            recreate_time = datetime.now()
            # TODO: no sens to drop entire collection every time, just update or drop for one USOS
            self.dao.drop_collection(constants.COLLECTION_COURSES_CLASSTYPES)
            for usos in self.dao.get_usoses():
                logging.info('recreating dictionaries in collections {0} for {1}'.format(constants.COLLECTION_COURSES_CLASSTYPES, usos[constants.USOS_ID]))
                inserts = []
                class_types = yield usoshelper.get_courses_classtypes(usos[constants.URL])
                if len(class_types) > 0:
                    for class_type in class_types.values():
                        class_type[constants.USOS_ID] = usos[constants.USOS_ID]
                        class_type[constants.CREATED_TIME] = recreate_time
                        class_type[constants.UPDATE_TIME] = recreate_time
                        inserts.append(class_type)
                    doc = self.dao.insert(constants.COLLECTION_COURSES_CLASSTYPES, inserts)
                else:
                    logging.info('fail to create {0} for {1}'.format(constants.COLLECTION_COURSES_CLASSTYPES, usos[constants.USOS_ID]))


    def prepare_database(self):
        if settings.CLEAN_DB:
            self.dao.drop_collections()

        if settings.UPDATE_DICTIONARIES:
            self.dao.drop_collection(constants.COLLECTION_USOSINSTANCES)
            for usos in settings.USOSINSTANCES:
                logging.info('adding usos: {0} '.format(usos[constants.USOS_ID]))
                doc = self.dao.find_usos(usos[constants.USOS_ID])
                if not doc:
                    self.dao.insert(constants.COLLECTION_USOSINSTANCES, usos)

    @tornado.gen.coroutine
    def initial_user_crowl(self, user_id):
        logging.debug('crawling for user id: {0}'.format(user_id))
        crowl_time = datetime.now()

        user = self.dao.get_user(user_id)
        if not user:
            logging.error("could not crowl for usos data for unknown user with id: {0}".format(user_id))
            return

        usos = self.dao.get_usos(user[constants.USOS_ID])

        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                              usos[constants.CONSUMER_SECRET],
                              user[constants.ACCESS_TOKEN_KEY], user[constants.ACCESS_TOKEN_SECRET])

        # user_info
        user_info = self.dao.get_users_info(user_id)
        if not user_info:
            result = updater.request_user_info()
            result[constants.USER_ID] = user_id
            result[constants.CREATED_TIME] = crowl_time
            doc = self.dao.insert(constants.COLLECTION_USERS_INFO, result)
            logging.debug('user_info for user_id {0} inserted: {1}'.format(user_id,doc))
        else:
            result = updater.request_user_info()
            result[constants.UPDATE_TIME] = crowl_time
            result[constants.USER_ID] = user_id
            result = self.dao.update(constants.COLLECTION_USERS_INFO, constants.ID, user_info[constants.ID], result)
            logging.debug('user_info updated: {0}'.format(user_info[constants.ID]))

        # course_editions
        courseseditions = self.dao.get_courses_editions(user_id)
        if not courseseditions:
            result = updater.request_courses_editions()
            result[constants.UPDATE_TIME] = crowl_time
            result[constants.USER_ID] = user_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            courseseditions = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
            logging.debug('course_editions inserted into courses_editions: {0}'.format(courseseditions))
        else:
            result = updater.request_courses_editions()
            result[constants.UPDATE_TIME] = crowl_time
            result[constants.USER_ID] = user_id
            result = self.dao.update(constants.COLLECTION_COURSES_EDITIONS, constants.ID, courseseditions[constants.ID], result)
            logging.debug('course_editions updated: {0}'.format(courseseditions[constants.ID]))


        # terms
        for term_id in self.dao.get_user_terms(user_id):

            term = self.dao.get_terms(term_id, user_id)
            result = yield usoshelper.get_term_info(usos[constants.URL], term_id)
            result = json.loads(result)
            result[constants.USER_ID] = user_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            if not term:
                result[constants.CREATED_TIME] = crowl_time
            else:
                result[constants.CREATED_TIME] = term[constants.CREATED_TIME]
                self.dao.remove(constants.COLLECTION_TERMS, constants.ID, term[constants.ID])
            result[constants.UPDATE_TIME] = crowl_time
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            doc = self.dao.insert(constants.COLLECTION_TERMS, result)
            if not term:
                logging.debug('term with term_id: {0} inserted with id: {1}'.format(term_id, doc))
            else:
                logging.debug('term with term_id: {0} updated with new id: {1}'.format(term_id, doc))

        # courses
        for course_id in self.dao.get_user_courses(user_id):
            course = self.dao.get_courses(course_id, user_id)
            result = yield usoshelper.get_course_info(usos[constants.URL], course_id)
            result = json.loads(result)
            result[constants.USER_ID] = user_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            if not course:
                result[constants.CREATED_TIME] = crowl_time
            else:
                result[constants.CREATED_TIME] = course[constants.CREATED_TIME]
                self.dao.remove(constants.COLLECTION_TERMS, constants.ID, term[constants.ID])
            result[constants.UPDATE_TIME] = crowl_time
            doc = self.dao.insert(constants.COLLECTION_COURSES, result)
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
            result[constants.USER_ID] = user_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            if not grades:
                result[constants.CREATED_TIME] = crowl_time
            else:
                result[constants.CREATED_TIME] = grades[constants.CREATED_TIME]
                self.dao.remove(constants.COLLECTION_GRADES, constants.ID, grades[constants.ID])
            result[constants.UPDATE_TIME] = crowl_time
            doc = self.dao.insert(constants.COLLECTION_GRADES, result)
            if not grades:
                logging.info('grades for term_id: {0} and course_id: {1} inserted with id: {2} '.format(term_id,course_id,doc))
            else:
                logging.info('grades for term_id: {0} and course_id: {1} updated with id: {2} '.format(term_id,course_id,doc))

            # participants
            result = dict()
            participants = self.dao.get_participants(course_id, term_id)
            result[constants.TERM_ID] = term_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            result[constants.COURSE_ID] = course_id
            result[constants.PARTICIPANTS] = participants
            if not participants:
                result[constants.CREATED_TIME] = crowl_time
            else:
                result[constants.CREATED_TIME] = participants[constants.CREATED_TIME]
                self.dao.remove(constants.COLLECTION_PARTICIPANTS, term_id, course_id)
            result[constants.UPDATE_TIME] = crowl_time
            doc = self.dao.insert(constants.COLLECTION_PARTICIPANTS, result)
            if not participants:
                logging.debug('participants for term_id: {0} and course_id: {1} inserted with id: {2}'.format(term_id,course_id,doc))
            else:
                logging.debug('participants for term_id: {0} and course_id: {1} updated with id: {2}'.format(term_id,course_id,doc))
            #units
            for unit_id in units:
                unit = self.dao.get_courses_units(unit_id)
                result = yield usoshelper.get_courses_units(usos[constants.URL], unit_id)
                result = json.loads(result)
                if not unit:
                    result[constants.USOS_ID] = usos[constants.USOS_ID]
                    result[constants.CREATED_TIME] = crowl_time
                else:
                    result[constants.CREATED_TIME] = unit[constants.CREATED_TIME]
                    self.dao.remove(constants.COLLECTION_COURSES_UNITS, constants.UNIT_ID, unit)
                doc = self.dao.insert(constants.COLLECTION_COURSES_UNITS, result)
                if not unit:
                    logging.debug('unit {0} inserted with id: {1}'.format(unit_id, doc))
                else:
                    logging.debug('unit {0} updated for id: {1}'.format(unit_id, doc))


        # crowl collection
        result = dict()
        result[constants.USER_ID] = user_id
        result[constants.CREATED_TIME] = crowl_time
        result[constants.UPDATE_TIME] = datetime.now()

        doc = self.dao.insert(constants.COLLECTION_CROWLLOG, result)
        logging.debug('crowl log inserted with id {0}'.format(doc))