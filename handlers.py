import sys

import motor
import tornado.web
from bson import json_util

import constants
from usosupdater import USOSUpdater


class Parameters:
    def __init__(self, usos_id, user_id, access_token_key, access_token_secret):
        self.usos_id = usos_id
        self.user_id = user_id
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_parameters(self):
        return Parameters(
                self.get_argument(constants.USOS_ID, default=None, strip=True),
                self.get_argument(constants.USER_ID, default=None, strip=True),
                self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True),
                self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True),
        )

    def validate_parameters(self, expected):
        if len(self.request.arguments) != expected:
            # TODO: nie wypisuje tego arguments not suppored
            raise tornado.web.HTTPError(404, "<html><body>Arguments not supported {0}</body></html>".format(
                str(self.request.arguments)))

    def validate_usos(self, usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(404,
                                        "<html><body>Usos %s not supported</body></html>".format(parameters.usos_id))


class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world from database {0}".format(self.db.name))


class UserHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)

        parameters = self.get_parameters()

        # TODO: moim zdaniem nie ma sensu za kazdym razem pytac baze o usosa to tylko spowalnia
        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})
        self.validate_usos(usos, parameters)

        user_id = self.get_argument(constants.USER_ID, default=None, strip=True)

        doc = yield self.db.users.find_one({constants.USER_ID: parameters.user_id})

        if not doc:
            updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                                  parameters.access_token_key, parameters.access_token_secret)

            result = updater.request_user_info()

            doc_id = yield motor.Op(self.db.users.insert, {constants.USER_ID: parameters.user_id,
                                                           constants.USOS_DATA: result})

            print "no user with id: {0} in mongo, fetched from usos and created with id: {1}".format(parameters.user_id,
                                                                                                     doc_id)

            doc = yield self.db.users.find_one({constants.USER_ID: parameters.user_id})
        else:
            print "get course for ", user_id , " from mongo with id:", doc["_id"]

        self.write(json_util.dumps(doc))


class CoursesHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)
        parameters = self.get_parameters()
        # TODO: po co za kazdym razem ?
        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})
        self.validate_usos(usos, parameters)

        user_id = self.get_argument(constants.USER_ID, default=None, strip=True)

        doc = yield self.db.courses.find_one({constants.USER_ID: parameters.user_id})

        if not doc:
            updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                                  parameters.access_token_key, parameters.access_token_secret)
            result = updater.request_curse_info()

            doc_id = yield motor.Op(self.db.courses.insert, {constants.USER_ID: user_id,
                                                             constants.USOS_DATA: result})
            print "no courses for user_id: {0} in mongo, fetched from usos and created with id: {1}".format(
                    user_id, doc_id)

            doc = yield self.db.courses.find_one({constants.USER_ID: parameters.user_id})
        else:
            print "get courses for ", user_id , " from mongo with id:", doc["_id"]

        self.write(json_util.dumps(doc))


class GradesForCourseAndTermHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(6)
        parameters = self.get_parameters()
        # TODO: po co za kazdym razem?
        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})

        self.validate_usos(usos, parameters)

        user_id = self.get_argument(constants.USER_ID, default=None, strip=True)
        course_id = self.get_argument(constants.COURSE_ID, default=None, strip=True)
        term_id = self.get_argument(constants.TERM_ID, default=None, strip=True)

        doc = yield self.db.grades.find_one(
                {constants.USER_ID: parameters.user_id, constants.COURSE_ID: course_id, constants.TERM_ID: term_id})

        if not doc:
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)
                result = updater.request_grades_for_course(course_id, term_id)
            except:
                e = sys.exc_info()[0]
                # TODO: ponizszego bledu nie wyswietla tylko wali 400, chyba lepiej to nalezy jakos obsluzyc
                raise tornado.web.HTTPError(400, "<html><body>Unexpected error: %s </body></html>".format(e.message))
                return

            doc_id = yield motor.Op(self.db.grades.insert, {constants.COURSE_ID: course_id,
                                                            constants.TERM_ID: term_id,
                                                            constants.USER_ID: parameters.user_id,
                                                            constants.USOS_DATA: result})
            print "no grades for user_id: {0} course_id: {1} term_id: {2} in mongo, fetched from usos and created with id: {4}".format(
                    user_id, course_id, term_id, parameters.user_id, doc_id)

            doc = yield self.db.grades.find_one(
                    {constants.USER_ID: parameters.user_id, constants.COURSE_ID: course_id, constants.TERM_ID: term_id})
        else:
            print "get grades for ", user_id , " from mongo with id:", doc["_id"]

        self.write(json_util.dumps(doc))


class GradesForAllCoursesAndTermsHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        pass
        # TODO:
