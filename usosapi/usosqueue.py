import logging
from datetime import datetime
import json

import tornado.gen
import tornado.options
from tornado.queues import LifoQueue
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging

import constants
from mongo_utils import Dao
from usosupdater import USOSUpdater
import usoshelper


class UsosQueue():
    dao = Dao()
    user_queue = LifoQueue()

    def put_user(self, user_id):
        self.user_queue.put(user_id)

    @tornado.gen.coroutine
    def crowl(self, user_id):
        logging.info('crawling for: {0}'.format(user_id))
        user = self.dao.get_user(user_id)
        usos = self.dao.get_usos(user[constants.USOS_ID])

        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                              usos[constants.CONSUMER_SECRET],
                              user[constants.ACCESS_TOKEN_KEY], user[constants.ACCESS_TOKEN_SECRET])

        logging.info('request_user_info fetch for : {0}'.format(user_id))
        result = updater.request_user_info()
        result[constants.USER_ID] = user_id
        result[constants.CREATED_TIME] = datetime.now()

        logging.info('request_user_info result: {0}'.format(result))
        doc = self.dao.insert(constants.COLLECTION_USERS_INFO, result)
        logging.info('request_user_info inserted: {0}'.format(doc))

        logging.info('request_curseseditions_info for: {0}'.format(user_id))
        result = updater.request_curseseditions_info()
        result[constants.USER_ID] = user_id
        result[constants.CREATED_TIME] = datetime.now()
        logging.info('request_curseseditions_info result: {0}'.format(result))

        doc = self.dao.insert(constants.COLLECTION_CURSES_EDITIONS, result)
        logging.info('request_user_info inserted: {0}'.format(doc))

        for term_id in self.dao.get_user_terms(user_id):
            logging.info('requesting term info for url {0} and term_id'.format(usos[constants.URL], term_id))
            result = yield usoshelper.get_term_info(usos[constants.URL], term_id)
            result = json.loads(result)
            result[constants.USER_ID] = user_id
            result[constants.CREATED_TIME] = datetime.now()
            result[constants.USOS_ID] = usos[constants.USOS_ID]

            logging.info('requesting term info result {0}'.format(result))
            doc = self.dao.insert(constants.COLLECTION_TERMS, result)
            logging.info('term inserted with id {0}'.format(doc))

        for course_id in self.dao.get_user_courses(user_id):
            logging.info('requesting get_course_info for url {0} and term_id {1}'.format(usos[constants.URL], course_id))

            result = yield usoshelper.get_course_info(usos[constants.URL], course_id)
            result = json.loads(result)
            result[constants.USER_ID] = user_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            result[constants.CREATED_TIME] = datetime.now()

            logging.info('get_course_info result {0}'.format(result))
            doc = self.dao.insert(constants.COLLECTION_COURSES, result)
            logging.info('course info inserted with id {0}'.format(doc))

        for data in self.dao.get_user_terms_and_courses(user_id):
            term_id, course_id = str(data[0]), str(data[1])
            logging.info('requesting grade for term_id {0} and user_id {1}'.format(term_id, course_id))
            result = updater.request_grades_for_course(course_id, term_id)

            #result[user_id] = user_id
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            result[constants.CREATED_TIME] = datetime.now()

            logging.info('grade for term_id {0} and user_id {1} {2}'.format(term_id, course_id, result))
            doc = self.dao.insert(constants.COLLECTION_GRADES, result)
            logging.info('grades inserted with id {0}'.format(doc))


    @tornado.gen.coroutine
    def queue_watcher(self):
        while True:
            users_id = yield self.user_queue.get()
            self.crowl(users_id)

@tornado.gen.coroutine
def main():
    from bson.objectid import ObjectId
    existing_user_id = ObjectId("56ac61f23d78210722816521")
    u = UsosQueue()
    yield u.crowl(existing_user_id)

    #d = Dao()
    #print 'terms:',  d.get_user_terms(existing_user_id)
    #print 'courses:',  d.get_user_courses(existing_user_id)
    #print 'terms and courses', d.get_user_terms_and_courses(existing_user_id)


if __name__ == "__main__":
    logging.basicConfig()
    tornado.options.parse_command_line()
    enable_pretty_logging()

    IOLoop.current().run_sync(main)
