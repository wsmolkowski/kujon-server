import json
import logging
from datetime import datetime
from bson.objectid import ObjectId

import tornado.gen

from usosapi import constants
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

    def append(self, data, user_id, usos_id, create_time, update_time):
        if not data:
            data = dict()

        if user_id:
            data[constants.USER_ID] = user_id

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
            class_types = yield usoshelper.get_courses_classtypes(usos[constants.URL])
            if len(class_types) > 0:
                for class_type in class_types.values():
                    class_type[constants.USOS_ID] = usos[constants.USOS_ID]
                    class_type[constants.CREATED_TIME] = recreate_time
                    class_type[constants.UPDATE_TIME] = recreate_time
                    inserts.append(class_type)
                doc = self.dao.insert(constants.COLLECTION_COURSES_CLASSTYPES, inserts)
            else:
                raise Exception(
                    'fail to recreate_dictionaries {0} for {1}'.format(constants.COLLECTION_COURSES_CLASSTYPES,
                                                                       usos[constants.USOS_ID]))
        raise tornado.gen.Return(True)

    def drop_collections(self):
        self.dao.drop_collections()

    def recreate_usos(self):
        self.dao.drop_collection(constants.COLLECTION_USOSINSTANCES)
        for usos in usosinstances.USOSINSTANCES:
            logging.info('adding usos: {0} '.format(usos[constants.USOS_ID]))
            doc = self.dao.find_usos(usos[constants.USOS_ID])
            if not doc:
                self.dao.insert(constants.COLLECTION_USOSINSTANCES, usos)

    @tornado.gen.coroutine
    def initial_user_crowl(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

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
        result = updater.request_user_info()
        result = self.append(result, user_id, None, crowl_time, crowl_time)
        ui_doc = self.dao.insert(constants.COLLECTION_USERS_INFO, result)
        logging.debug('user_info inserted: {0}'.format(ui_doc))

        # course_editions
        result = updater.request_courses_editions()
        result = self.append(result, user_id, usos[constants.USOS_ID], crowl_time, crowl_time)

        ce_doc = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
        logging.debug('course_editions inserted: {0}'.format(ce_doc))

        # terms
        for term_id in self.dao.get_user_terms(user_id):
            result = yield usoshelper.get_term_info(usos[constants.URL], term_id)
            result = self.append(result, user_id, usos[constants.USOS_ID], crowl_time, crowl_time)

            t_doc = self.dao.insert(constants.COLLECTION_TERMS, result)
            logging.debug('terms inserted: {0}'.format(t_doc))

        # courses
        for course_id in self.dao.get_user_courses(user_id):
            result = yield usoshelper.get_course_info(usos[constants.URL], course_id)
            result = self.append(result, user_id, usos[constants.USOS_ID], crowl_time, crowl_time)

            c_doc = self.dao.insert(constants.COLLECTION_COURSES, result)
            logging.debug('course inserted: {0}'.format(c_doc))

        # grades and participants and units
        for data in self.dao.get_user_courses_editions(user_id):
            term_id, course_id = str(data[0]), str(data[1])

            result = updater.request_grades_for_course(course_id, term_id)
            participants = result.pop('participants')
            units = result.pop('course_units_ids')
            result = self.append(result, user_id, usos[constants.USOS_ID], crowl_time, crowl_time)

            g_doc = self.dao.insert(constants.COLLECTION_GRADES, result)
            logging.debug('grades inserted: {0}'.format(g_doc))

            # participants
            result = self.append(dict(), user_id, usos[constants.USOS_ID], crowl_time, crowl_time)
            result[constants.PARTICIPANTS] = participants

            p_doc = self.dao.insert(constants.COLLECTION_PARTICIPANTS, result)
            logging.debug('participants inserted: {0}'.format(p_doc))

            # units
            for unit_id in units:
                result = yield usoshelper.get_courses_units(usos[constants.URL], unit_id)
                result = self.append(result, user_id, usos[constants.USOS_ID], crowl_time, crowl_time)

                u_doc = self.dao.insert(constants.COLLECTION_COURSES_UNITS, result)
                logging.debug('units inserted: {0}'.format(u_doc))

        # crowl collection
        result = dict()
        result[constants.USER_ID] = user_id
        result[constants.CREATED_TIME] = crowl_time
        result[constants.UPDATE_TIME] = datetime.now()

        doc = self.dao.insert(constants.COLLECTION_CROWLLOG, result)
        logging.info('crowl log inserted with id {0}'.format(doc))

if __name__ == "__main__":
    u = UsosCrowler()
    u.initial_user_crowl(ObjectId("56b267cfc4f9d22360be77fc"))