import motor
import tornado.web
from bson import json_util
import constants
from usosupdater import USOSUpdater
from handlers_api import BaseHandler

class CoursesHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)
        parameters = self.get_parameters()

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key},
                                                constants.USER_PRESENT_KEYS)

        if not user_doc:
            raise tornado.web.HTTPError(400, "<html><body>User not authenticated</body></html>")

        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})

        course_doc = yield self.db.courses.find_one({constants.MOBILE_ID: parameters.mobile_id})

        if not course_doc:
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_curse_info(user_doc[constants.USOS_ID])
            except Exception, ex:
                raise tornado.web.HTTPError(400, "Exception while fetching USOS data for course info %s".format(ex))

            result[constants.MOBILE_ID] = user_doc[constants.MOBILE_ID]
            doc_id = yield motor.Op(self.db.courses.insert, result)
            print "no courses for mobile_id: {0} in mongo, fetched from usos and created with id: {1}".format(
                    parameters.mobile_id, doc_id)

            course_doc = yield self.db.courses.find_one({constants.MOBILE_ID: parameters.mobile_id})
        else:
            print "get courses for mobile_id: {0} from mongo with id: {1}".format(parameters.mobile_id,
                                                                                  course_doc["_id"])

        self.write(json_util.dumps(course_doc))

