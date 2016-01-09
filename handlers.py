from datetime import datetime

import motor
import tornado.web
from bson import json_util

import settings
from usosupdater import USOSUpdater

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world from database {0}".format(self.db.name))


class SchoolHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, school_id):
        '''
        if school in db return school
        else
            1. fetch school data from usos server
            2. return data to client
            3. save data in db
        :param school_id:
        :return: dictonary representing school
        '''


        doc = yield self.db.schools.find_one({'school_id': school_id})

        if not doc:
            school = {'school_id': school_id, 'type': 0, 'version': 1}

            doc_id = yield motor.Op(self.db.schools.insert, school)
            print 'new school created with id:', doc_id

            doc = yield self.db.schools.find_one({'school_id': school_id})

        self.write(json_util.dumps(doc))



class UserHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_id):

        doc = yield self.db.users.find_one({'user_id': user_id})

        if not doc:
            access_token_key = '3ShYQv8LyvgeXthKJzmJ'
            access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'

            updater = USOSUpdater('https://usosapps.uw.edu.pl/', 'KBt6uWPWUekUzFtNTyY9', 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG', access_token_key, access_token_secret)
            result = updater.request_user_info()

            doc_id = yield motor.Op(self.db.users.insert, {'user_id': user_id, 'usos_data': result})
            print 'new user created with id:', doc_id

            doc = yield self.db.users.find_one({'user_id': user_id})
        else:
            print 'user from mongo with id:', doc.user_id

        self.write(json_util.dumps(doc))


class ScheduleHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, user_id, start_date):
        start_date = datetime.strptime(start_date, settings.DATE_FORMAT)
        end_date = start_date + datetime.timedelta(days=settings.DEFAULT_SCHEDULE_PERIOD)

        schedule = {
            '2016-01-04': {
                '1238': {
                    'start_time': '07:00',
                    'end_time': '09:00',
                    'type': 'egzamin',
                    'room': '5959',
                },
                '1238': {
                    'start_time': '09:00',
                    'end_time': '11:00',
                    'type': 'wyklad',
                    'room': '8173',
                }

            },
            '2016-01-05': {
                '1238': {
                    'start_time': '07:00',
                    'end_time': '09:00',
                    'type': 'lab',
                    'room': '5959',
                }
            }
        }
        self.write(schedule)


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
