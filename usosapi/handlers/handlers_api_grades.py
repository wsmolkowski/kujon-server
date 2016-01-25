from urllib import unquote

import motor
import tornado.web
from bson import json_util

from usosapi import constants
from handlers_api import BaseHandler
from usosapi.usosupdater import USOSUpdater


class GradesForCourseAndTermHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        parameters = self.get_parameters()

        usos = self.get_usos(parameters.user_usos_id)

        user_doc = self.get_current_user()
        if not user_doc:
            user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key},
                                                constants.USER_PRESENT_KEYS)
        if not user_doc:
            raise tornado.web.HTTPError(400, "<html><body>User not authenticated</body></html>")

        course_id = self.get_argument(constants.COURSE_ID, default=None, strip=True)
        term_id = self.get_argument(constants.TERM_ID, default=None, strip=True)
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

            result[constants.USOS_ID] = parameters.usos_id
            result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.TERM_ID] = term_id
            result[constants.COURSE_ID] = course_id
            doc_id = yield motor.Op(self.db.grades.insert, result)

            print "no grades for mobile_id: {0} course_id: {1} term_id: {2} in mongo, fetched from usos and created with id: {3}".format(
                    parameters.mobile_id, course_id, term_id, doc_id)
            doc = result
        else:
            print "get grades for mobile_id: {0} from mongo with id: {1}".format(parameters.mobile_id, doc["_id"])

        self.write(json_util.dumps(doc))
