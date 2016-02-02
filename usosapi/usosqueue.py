import json
import logging
from datetime import datetime

import tornado.gen
import tornado.options
from bson.objectid import ObjectId
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
from tornado.queues import LifoQueue

import constants
import usoshelper
from mongo_utils import Dao
from usosupdater import USOSUpdater


class UsosQueue():
    dao = Dao()
    user_queue = LifoQueue()

    def put_user(self, user_id):
        self.user_queue.put(user_id)

    @tornado.gen.coroutine
    def crowl(self, user_id):
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
            logging.info('user_info for user_id {0} inserted: {1}'.format(user_id,doc))
        else:
            result = updater.request_user_info()
            result[constants.UPDATE_TIME] = crowl_time
            result[constants.USER_ID] = user_id
            result = self.dao.update(constants.COLLECTION_USERS_INFO, constants.ID, user_info[constants.ID], result)
            logging.info('user_info updated: {0}'.format(user_info[constants.ID]))

        # course_editions
        courseseditions = self.dao.get_courses_editions(user_id)
        if not courseseditions:
            result = updater.request_courses_editions()
            result[constants.UPDATE_TIME] = crowl_time
            result[constants.USER_ID] = user_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            courseseditions = self.dao.insert(constants.COLLECTION_COURSES_EDITIONS, result)
            logging.info('course_editions inserted into courses_editions: {0}'.format(courseseditions))
        else:
            result = updater.request_courses_editions()
            result[constants.UPDATE_TIME] = crowl_time
            result[constants.USER_ID] = user_id
            result = self.dao.update(constants.COLLECTION_COURSES_EDITIONS, constants.ID, courseseditions[constants.ID], result)
            logging.info('course_editions updated: {0}'.format(courseseditions[constants.ID]))


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
                logging.info('term with term_id: {0} inserted with id: {1}'.format(term_id, doc))
            else:
                logging.info('term with term_id: {0} updated with new id: {1}'.format(term_id, doc))

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
                logging.info('course with course_id: {0} inserted with id: {1}'.format(course_id, doc))
            else:
                logging.info('course with course_id: {0} updated with new id: {1} '.format(course_id, doc))

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
            partic = self.dao.get_participants(course_id, term_id)
            result[constants.TERM_ID] = term_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            result[constants.COURSE_ID] = course_id
            result[constants.PARTICIPANTS] = participants
            if not partic:
                result[constants.CREATED_TIME] = crowl_time
            else:
                result[constants.CREATED_TIME] = partic[constants.CREATED_TIME]
                self.dao.remove(constants.COLLECTION_PARTICIPANTS, term_id, course_id)
            result[constants.UPDATE_TIME] = crowl_time
            doc = self.dao.insert(constants.COLLECTION_PARTICIPANTS, result)
            if not partic:
                logging.info('participants for term_id: {0} and course_id: {1} inserted with id: {2}'.format(term_id,course_id,doc))
            else:
                logging.info('participants for term_id: {0} and course_id: {1} updated with id: {2}'.format(term_id,course_id,doc))
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
                    logging.info('unit {0} inserted with id: {1}'.format(unit_id, doc))
                else:
                    logging.info('unit {0} updated for id: {1}'.format(unit_id, doc))


        # crowl collection
        result = dict()
        result[constants.USER_ID] = user_id
        result[constants.CREATED_TIME] = crowl_time
        result[constants.UPDATE_TIME] = datetime.now()

        doc = self.dao.insert(constants.COLLECTION_CROWLLOG, result)
        logging.debug('crowl log inserted with id {0}'.format(doc))

    @tornado.gen.coroutine
    def queue_watcher(self):
        while True:
            users_id = yield self.user_queue.get()
            self.crowl(users_id)

    @tornado.gen.coroutine
    def update_usoses_dictionaries(self):
        crowl_time = datetime.now()



        # courses_classtypes
        self.dao.drop_collection('courses_classtypes')
        for usos in self.dao.get_usoses():
            logging.info('Loading dictionaries for USOS: {0}'.format(usos[constants.USOS_ID]))

            result = yield usoshelper.get_courses_classtypes(usos[constants.URL])
            result = json.loads(result)
            r2 = []
            for r in result:
                rek = result[r]
                rek[constants.USOS_ID] = usos[constants.USOS_ID]
                r2.append(rek)

            doc = self.dao.insert(constants.COLLECTION_COURSES_CLASSTYPES, r2)
            logging.info('courses_classtypes for usos {0} inserted.'.format(usos[constants.USOS_ID]))

@tornado.gen.coroutine
def main():

    uqueue = UsosQueue()

    yield uqueue.update_usoses_dictionaries()


    existing_user_id = ObjectId("56ae5a793d7821151c33954d")
    yield uqueue.crowl(existing_user_id)
    existing_user_id = ObjectId("56ae69173d7821151c339550")
    yield uqueue.crowl(existing_user_id)



if __name__ == "__main__":
    logging.basicConfig()
    tornado.options.parse_command_line()
    enable_pretty_logging()

    IOLoop.current().run_sync(main)
