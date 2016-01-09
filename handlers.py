from datetime import datetime
import motor
import tornado.web
from bson import json_util
import sys

from usosupdater import USOSUpdater
from usosinstance import UsosInstances, UsosInstance
import settings



class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world from database {0}".format(self.db.name))


class UserHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        if len(self.request.arguments) != 4:
            self.write("arguments not supported")
            print "arguments not supported: ", self.request.arguments
            return
        else:
            try:
                usos_id = self.request.arguments['usos_id'][0]
                usoses = UsosInstances()
                usos = usoses.getbyid(usos_id)
                if not usos:
                    self.write("usos not supported")
                    print "usos not supported: ", usos_id
                    return
                user_id = self.request.arguments['user_id'][0]
                access_token_key = self.request.arguments['access_token_key'][0]
                access_token_secret = self.request.arguments['access_token_secret'][0]
            except KeyError:
                print "unexpexted error during parsing args:", sys.exc_info()[0]
                self.write("arguments not supported")
                return

        try:
            doc = yield self.db.users.find_one({'user_id': user_id})
        except:
            pass

        if not doc:

            updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, access_token_key, access_token_secret)
            result = updater.requestUser()

            doc_id = yield motor.Op(self.db.users.insert, {'user_id': user_id, 'usos_data': result})
            print 'no user with id: ',user_id,' fetched from usos and user created in mongo with id:', doc_id

            doc = yield self.db.users.find_one({'user_id': user_id})
        else:
            print 'get user from mongo with id:', doc['_id']

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
        #         usos_id = self.request.arguments['usos_id'][0]
        #         usoses = UsosInstances()
        #         usos = usoses.getbyid(usos_id)
        #         if not usos:
        #             self.write("usos not supported")
        #             print "usos not supported: ", usos_id
        #             return
        #         user_id = self.request.arguments['user_id'][0]
        #         access_token_key = self.request.arguments['access_token_key'][0]
        #         access_token_secret = self.request.arguments['access_token_secret'][0]
        #     except KeyError:
        #         print "unexpexted error during parsing args:", sys.exc_info()[0]
        #         self.write("arguments not supported")
        #         return
        #
        # try:
        #     doc = yield self.db.users.find_one({'user_id': user_id})
        # except:
        #     pass
        #
        # if not doc:
        #
        #     updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, access_token_key, access_token_secret)
        #     result = updater.requestUser()
        #
        #     doc_id = yield motor.Op(self.db.users.insert, {'user_id': user_id, 'usos_data': result})
        #     print 'no user with id: ',user_id,' fetched from usos and user created in mongo with id:', doc_id
        #
        #     doc = yield self.db.users.find_one({'user_id': user_id})
        # else:
        #     print 'get user from mongo with id:', doc['_id']

        usoses = UsosInstances()
        usos = usoses.getbyid("UW")
        access_token_key = "3ShYQv8LyvgeXthKJzmJ"
        access_token_secret = "JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y"
        updater = USOSUpdater(usos.url, usos.consumer_key, usos.consumer_secret, access_token_key, access_token_secret)
        result = updater.requestCourses()

        self.write(json_util.dumps(result))


class ClassGroupHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, classgroupid):
        classGroup = {
            'classGroupId': classgroupid,
            'start_time': '07:00',
            'end_time': '09:00',
            'type': 'egzamin',
            'place': '5959',
            'teacher': 'Jan Kiepuraa',
            'occurs': 'co tydzien'
        }
        self.write(classGroup)


class TermsHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        terms = {
            '112': {
                'name': 'Trymestr letni 2004/05',
                'start_date': '',
                'end_date': ''
            }
        }
        self.write(terms)


class CoursesHandlers(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        courses = {
            'courses': {
                '1000-612BDB': 'Bazy danych w bankowosci i zarzadzaniu',
                '1000-612BSK': 'Bezpieczenstwo sieci komputerowych'
            }
        }

        self.write(courses)


class CourseEditionsHandlers(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        course = {
            'id': '1000-612BDB',
            'edition': '123123123',
            'name': 'Bazy danych w bankowosci i zarzadzaniu',
            'desciption': '1. Tekstowe bazy danych. Dokumenty el.....'
        }
        self.write(course)
