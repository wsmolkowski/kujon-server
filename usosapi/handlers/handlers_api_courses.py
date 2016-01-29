import logging

import motor
import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants
from usosapi import usosupdater
from usosapi import usoshelper

class CourseHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, courseId):

        parameters = self.get_parameters()

        try:
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})
        except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching user data %s".format(ex))

        if not courseId:
            raise tornado.web.HTTPError(400,
                                        "Don't have given courseId for user: ".format(courseId, parameters.mobile_id))

        courseDoc = yield self.db.courses.find_one({constants.COURSE_ID: courseId,
                                                    constants.USOS_ID: user_doc[constants.USOS_ID]})

        if not courseDoc:
            usos = self.get_usos(user_doc[constants.USOS_ID])
            logging.info("Course with courseId: {0} not found in mongo for user: {1}, fetching from usos.".format(
                    courseId, parameters.mobile_id))

            courseDoc = yield usoshelper.get_course_info(usos[constants.URL], courseId)

            try:
                courseDoc = json_util.loads(courseDoc)
                courseDoc[constants.USOS_ID] = user_doc[constants.USOS_ID]
                courseDocId = yield motor.Op(self.db.courses.insert, courseDoc)
            except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while inserting courseId to mongo {0}.".format(ex.message))

            logging.info(
                    "Course with courseId: {0} for mobile_id: {1}, fetched from usos and created with id: {2}".format(
                            courseId, parameters.mobile_id,courseDocId))
        else:
            logging.info("Courses with courseId: {0} for mobile_id: {1} fetched from db with id: {2}".format(
                    courseId, parameters.mobile_id, courseDoc["_id"]))

        self.write(json_util.dumps(courseDoc))


class CoursesEditionsHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = self.get_parameters()

        try:
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})
        except Exception, ex:
            raise tornado.web.HTTPError(400, "Exception while fetching user data %s".format(ex))
        if not user_doc:
            raise tornado.web.HTTPError(400, "User: {0} not found.".format(parameters.mobile_id))

        usos = self.get_usos(user_doc[constants.USOS_ID])

        course_doc = yield self.db.courseseditions.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                             constants.USOS_ID: user_doc[constants.USOS_ID]})

        if not course_doc:
            try:
                updater = usosupdater.USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_curseseditions_info()
            except Exception, ex:
                raise tornado.web.HTTPError(400, "Exception while fetching USOS data for course info: {0}".format(ex))

            result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.USER_USOS_ID] = parameters.user_usos_id

            doc_id = yield motor.Op(self.db.courseseditions.insert, result)
            logging.info("no courses for mobile_id: {0} in db. fetched from usos and saved with id: {1}".format(
                    parameters.mobile_id, doc_id))
            course_doc = result
        else:
            logging.info("get courses for mobile_id: {0} from db with id: {1}".format(parameters.mobile_id,
                                                                                      course_doc["_id"]))

        self.write(json_util.dumps(course_doc))
