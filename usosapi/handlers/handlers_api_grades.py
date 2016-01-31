import logging

import motor
import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.usosupdater import USOSUpdater


class GradesForUserHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = self.get_parameters()

        try:
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})
        except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching user data: {0}".format(ex.message))
        usos = self.get_usos(user_doc[constants.USOS_ID])

        try:
            doc = yield self.db.grades.find(
                {constants.USER_ID: ObjectId(user_doc[constants.USERS_ID])}, {"grades": 1})
        except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching grades: {0}".format(ex.message))

        if not doc:
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_grades_for_course(course_id, term_id)
            except Exception, ex:
                raise tornado.web.HTTPError(400, log_message=ex.message)

            result[constants.USOS_ID] = user_doc[constants.USOS_ID]
            result[constants.MOBILE_ID] = user_doc[constants.MOBILE_ID]
            result[constants.TERM_ID] = term_id
            result[constants.COURSE_ID] = course_id
            doc_id = yield motor.Op(self.db.grades.insert, result)

            logging.info(
                    "no grades for mobile_id: {0} course_id: {1} term_id: {2} in db, fetched from usos and saved with id: {3}".format(
                            parameters.mobile_id, course_id, term_id, doc_id))
            doc = result
        else:
            logging.info("get grades for mobile_id: {0} from db with id: {1}".format(parameters.mobile_id, doc["_id"]))

        self.write(json_util.dumps(doc))

class GradesForCourseAndTermHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        parameters = self.get_parameters()

        try:
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})
        except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching user data: {0}".format(ex))

        usos = self.get_usos(user_doc[constants.USOS_ID])
        doc = yield self.db.grades.find_one(
                {constants.MOBILE_ID: parameters.mobile_id, constants.COURSE_ID: course_id, constants.TERM_ID: term_id})

        if not doc:
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_grades_for_course(course_id, term_id)
            except Exception, ex:
                raise tornado.web.HTTPError(400, log_message=ex.message)

            result[constants.USOS_ID] = user_doc[constants.USOS_ID]
            result[constants.MOBILE_ID] = user_doc[constants.MOBILE_ID]
            result[constants.TERM_ID] = term_id
            result[constants.COURSE_ID] = course_id
            doc_id = yield motor.Op(self.db.grades.insert, result)

            logging.info(
                    "no grades for mobile_id: {0} course_id: {1} term_id: {2} in db, fetched from usos and saved with id: {3}".format(
                            parameters.mobile_id, course_id, term_id, doc_id))
            doc = result
        else:
            logging.info("get grades for mobile_id: {0} from db with id: {1}".format(parameters.mobile_id, doc["_id"]))

        self.write(json_util.dumps(doc))
