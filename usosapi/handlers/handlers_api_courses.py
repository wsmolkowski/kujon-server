import logging

import motor
import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.usosupdater import USOSUpdater


class CourseHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, courseId):
        parameters = self.get_parameters()

        if not courseId:
            raise tornado.web.HTTPError(400,
                                        "Don't have given courseId for user: ".format(courseId, parameters.mobile_id))

        # najperw sprawdzamy czy jest ten kurs, jak nie ma scigamy wszystkie i jeszcze raz sprawdzamy
        course_doc = yield self.db.courses.find_one({constants.COURSE_ID: courseId})

        if not course_doc:
            usos = self.get_usos(parameters.user_usos_id)
            logging.info("Course with courseId: {0} not found in mongo for user: {1}, fetching from usos.".format(
                    courseId, parameters.mobile_id))
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_course_info(courseId)
            except Exception, ex:
                raise tornado.web.HTTPError(400, "Exception while fetching USOS data for course info %s".format(ex))

            doc_id = yield motor.Op(self.db.courses.insert, result)
            logging.info(
                    "Course with courseId: {0} for mobile_id: {1}, fetched from usos and created with id: {2}".format(
                            courseId, parameters.mobile_id, doc_id))
            course_doc = result
        else:
            logging.info("Courses with courseId: {0} for mobile_id: {1} fetched from db with id: {2}".format(
                    courseId, parameters.mobile_id, course_doc["_id"]))

        self.write(json_util.dumps(course_doc))


class CoursesEditionsHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = self.get_parameters()

        usos = self.get_usos(parameters.user_usos_id)

        course_doc = yield self.db.courseseditions.find_one({constants.MOBILE_ID: parameters.mobile_id})

        if not course_doc:
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_curseseditions_info()
            except Exception, ex:
                raise tornado.web.HTTPError(400, "Exception while fetching USOS data for course info %s".format(ex))

            result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.USER_USOS_ID] = parameters.user_usos_id
            # result[constants.USOS_ID] = user_doc[constants.USOS_ID]
            doc_id = yield motor.Op(self.db.courseseditions.insert, result)
            logging.info("no courses for mobile_id: {0} in db. fetched from usos and saved with id: {1}".format(
                    parameters.mobile_id, doc_id))
            course_doc = result
        else:
            logging.info("get courses for mobile_id: {0} from db with id: {1}".format(parameters.mobile_id,
                                                                                      course_doc["_id"]))

        self.write(json_util.dumps(course_doc))