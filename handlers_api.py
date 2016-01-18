from datetime import datetime
import urlparse

import motor
import tornado.web
from bson import json_util

import constants
from usosupdater import USOSUpdater
import oauth2 as oauth

class Parameters:
    def __init__(self, usos_id, mobile_id, access_token_key, access_token_secret):
        self.usos_id = usos_id
        self.mobile_id = mobile_id
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie(constants.USER_SECURE_COOKIE)

    def get_parameters(self):
        return Parameters(
                self.get_argument(constants.USOS_ID, default=None, strip=True),
                int(self.get_argument(constants.MOBILE_ID, default=None, strip=True)),
                self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True),
                self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True),
        )

    def validate_parameters(self, expected):
        if len(self.request.arguments) != expected:
            raise tornado.web.HTTPError(404, "<html><body>Arguments not supported %s</body></html>".format(
                str(self.request.arguments)))

    def validate_usos(self, usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(404,
                                        "<html><body>Usos %s not supported</body></html>".format(parameters.usos_id))

    def get_token(self, content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

class UserHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)

        parameters = self.get_parameters()

        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})
        self.validate_usos(usos, parameters)

        user_doc = self.get_current_user()

        if not user_doc:
            try:
                print usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],\
                    parameters.access_token_key, parameters.access_token_secret
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)

                result = updater.request_user_info()
            except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching USOS data for user info %s".format(ex))

            result[constants.USOS_ID] = result.pop('id')
            result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.ACCESS_TOKEN_SECRET] = parameters.access_token_secret
            result[constants.ACCESS_TOKEN_KEY] = parameters.access_token_key
            result[constants.CREATED_TIME] = datetime.now()

            user_doc = yield motor.Op(self.db.users.insert, result)

            print "saved new user in database: {0}".format(user_doc)
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key},
                                                 constants.USER_PRESENT_KEYS)
        else:
            print "user data fetched from database {0}".format(user_doc)

        self.write(json_util.dumps(user_doc))

class CoursesHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)
        parameters = self.get_parameters()

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key},
                                                 constants.USER_PRESENT_KEYS)

        if not user_doc or user_doc[constants.USOS_ID] != parameters.usos_id:
            raise tornado.web.HTTPError(404, "<html><body>User not authenticated</body></html>")

        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})

        course_doc = yield self.db.courses.find_one({constants.MOBILE_ID: parameters.mobile_id})

        if not course_doc:
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_curse_info(user_doc[constants.USOS_ID])
            except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching USOS data for course info %s".format(ex))

            result[constants.MOBILE_ID] = user_doc[constants.MOBILE_ID]
            doc_id = yield motor.Op(self.db.courses.insert, result)
            print "no courses for mobile_id: {0} in mongo, fetched from usos and created with id: {1}".format(
                    parameters.mobile_id, doc_id)

            course_doc = yield self.db.courses.find_one({constants.MOBILE_ID: parameters.mobile_id})
        else:
            print "get courses for mobile_id: {0} from mongo with id: {1}".format(parameters.mobile_id, course_doc["_id"])

        self.write(json_util.dumps(course_doc))


class GradesForCourseAndTermHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(6)
        parameters = self.get_parameters()
        # TODO: po co za kazdym razem?
        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})

        self.validate_usos(usos, parameters)

        user_doc = yield self.db.users.find_one({constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key},
                                                 constants.USER_PRESENT_KEYS)

        if not user_doc:
            raise tornado.web.HTTPError(404, "<html><body>User not authenticated</body></html>")

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
                raise tornado.web.HTTPError(500, "Exception while fetching USOS data for grades for the course %s".format(ex))

            result[constants.USOS_ID] = parameters.usos_id
            result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.TERM_ID] = term_id
            result[constants.COURSE_ID] = course_id
            doc_id = yield motor.Op(self.db.grades.insert, result)

            print "no grades for mobile_id: {0} course_id: {1} term_id: {2} in mongo, fetched from usos and created with id: {3}".format(
                    parameters.mobile_id, course_id, term_id, doc_id)

            doc = yield self.db.grades.find_one(
                    {constants.MOBILE_ID: parameters.mobile_id, constants.COURSE_ID: course_id, constants.TERM_ID: term_id})
        else:
            print "get grades for mobile_id: {0} from mongo with id: {1}".format(parameters.mobile_id, doc["_id"])

        self.write(json_util.dumps(doc))


class GradesForAllCoursesAndTermsHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        pass
        # TODO:
