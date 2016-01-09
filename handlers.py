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
            raise tornado.web.HTTPError(404, "<html><body>Arguments not supported {0}</body></html>".format(str(self.request.arguments)))

    def validate_usos(self, usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(404, "<html><body>Usos %s not supported</body></html>".format(parameters.usos_id))

class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world from database {0}".format(self.db.name))


class UserHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)

        parameters = self.get_parameters()

        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})

        self.validate_usos(usos, parameters)

        doc = yield self.db.users.find_one({constants.USER_ID: parameters.user_id})

        if not doc:
            updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                                  parameters.access_token_key, parameters.access_token_secret)

            result = updater.request_user_info()

            doc_id = yield motor.Op(self.db.users.insert, {constants.USER_ID: parameters.user_id,
                                                           constants.USOS_DATA: result})

            print "no user with id: {0} fetched from usos and user created with id: {1}".format(parameters.user_id, doc_id)

            doc = yield self.db.users.find_one({constants.USER_ID: parameters.user_id})
        else:
            print "get course from mongo with id:", doc["_id"]

        self.write(json_util.dumps(doc))


class GradesHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(5)

        parameters = self.get_parameters()

        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})

        self.validate_usos(usos, parameters)

        course_id = self.get_argument(constants.COURSE_ID, default=None, strip=True)

        doc = yield self.db.grades.find_one({constants.USER_ID: parameters.user_id, constants.COURSE_ID: course_id})

        if not doc:
            updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                                  parameters.access_token_key, parameters.access_token_secret)
            result = updater.request_grades_for_course(course_id)

            doc_id = yield motor.Op(self.db.grades.insert, {constants.COURSE_ID: course_id,
                                                            constants.USER_ID: parameters.user_id,
                                                            constants.USOS_DATA: result})
            print "no course with id: {0} fetched for user: {1} from usos and user created with id: {2}".format(
                    course_id, parameters.user_id, doc_id)

            doc = yield self.db.grades.find_one({constants.COURSE_ID: parameters.user_id})
        else:
            print "get user from mongo with id:", doc["_id"]

        self.write(json_util.dumps(doc))


class CoursesHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        # if len(self.request.arguments) != 4:
        #     self.write("arguments not supported")
        #     print "arguments not supported: ", self.request.arguments
        #     return
        # else:
        #     try:
        #         usos_id = self.request.arguments[constants.USOS_ID][0]
        #         usoses = UsosInstances()
        #         usos = usoses.getbyid(usos_id)
        #         if not usos:
        #             self.write("usos not supported")
        #             print "usos not supported: ", usos_id
        #             return
        #         user_id = self.request.arguments[constants.USER_ID][0]
        #         access_token_key = self.request.arguments[constants.ACCESS_TOKEN_KEY][0]
        #         access_token_secret = self.request.arguments[constants.ACCESS_TOKEN_SECRET][0]
        #     except KeyError:
        #         print "unexpexted error during parsing args:", sys.exc_info()[0]
        #         self.write("arguments not supported")
        #         return
        #
        # try:
        #     doc = yield self.db.users.find_one({constants.USER_ID: user_id})
        # except:
        #     pass
        #
        # if not doc:
        #
        #     updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, access_token_key, access_token_secret)
        #     result = updater.requestUser()
        #
        #     doc_id = yield motor.Op(self.db.users.insert, {constants.USER_ID: user_id, "usos_data": result})
        #     print "no user with id: ",user_id," fetched from usos and user created in mongo with id:", doc_id
        #
        #     doc = yield self.db.users.find_one({constants.USER_ID: user_id})
        # else:
        #     print "get user from mongo with id:", doc["_id"]

        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: "UW"})

        access_token_key = "3ShYQv8LyvgeXthKJzmJ"
        access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
        updater = USOSUpdater(usos.url, usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET], access_token_key, access_token_secret)
        result = updater.request_user_info()

        self.write(json_util.dumps(result))


class ClassGroupHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, classgroupid):
        classGroup = {
            "classGroupId": classgroupid,
            "start_time": "07:00",
            "end_time": "09:00",
            "type": "egzamin",
            "place": "5959",
            "teacher": "Jan Kiepuraa",
            "occurs": "co tydzien"
        }
        self.write(classGroup)


class TermsHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        terms = {
            "112": {
                "name": "Trymestr letni 2004/05",
                "start_date": "",
                "end_date": ""
            }
        }
        self.write(terms)


class CoursesHandlers(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        courses = {
            "courses": {
                "1000-612BDB": "Bazy danych w bankowosci i zarzadzaniu",
                "1000-612BSK": "Bezpieczenstwo sieci komputerowych"
            }
        }

        self.write(courses)


class CourseEditionsHandlers(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        course = {
            "id": "1000-612BDB",
            "edition": "123123123",
            "name": "Bazy danych w bankowosci i zarzadzaniu",
            "desciption": "1. Tekstowe bazy danych. Dokumenty el....."
        }
        self.write(course)
