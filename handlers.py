import json
from datetime import datetime

import tornado.web

import settings
import usos


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class SchoolHandler(tornado.web.RequestHandler):
    def get(self, school_id):
        school = {
            'school_id': school_id,
            'type': 0,
            'version': 1
        }

        self.write(school)


class Contacts(json.JSONEncoder):
    contacts = {}
    name = ""


class User:
    def __init__(self,user_id,access_token_key,access_token_secret):

        if not self.ifexists(user_id):
            self.register(user_id,access_token_key,access_token_secret)


    def ifexists(self):
        #sprawdzenie czy user istnieje
        return True

    def register(self):
        return True

    def updateuserdata(self):
        return True

class UserHandler(tornado.web.RequestHandler):


    def get(self, user_id):
        print "proba wyciagniacia info o userze: " + user_id
        url = "services/users/user?user_id="+user_id+"&fields=id|first_name|last_name|student_status|sex|email|student_programmes|student_number|has_email|titles"
        print url
        access_token_key = 'uXLyCGpp5zfHPH4z4brg'
        access_token_secret = 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'

        updater = usos.USOSUpdater(user_id, access_token_key, access_token_secret)
        result=updater.request(url);
        self.write(result)



class ScheduleHandler(tornado.web.RequestHandler):
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


class ClassGroup(tornado.web.RequestHandler):
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


class Terms(tornado.web.RequestHandler):
    def get(self):
        terms = {
            '112': {
                'name': 'Trymestr letni 2004/05',
                'start_date': '',
                'end_date': ''
            }
        }
        self.write(terms)


class Courses(tornado.web.RequestHandler):
    def get(self):
        courses = {
            'courses': {
                '1000-612BDB': 'Bazy danych w bankowosci i zarzadzaniu',
                '1000-612BSK': 'Bezpieczenstwo sieci komputerowych'
            }
        }


class CourseEditions(tornado.web.RequestHandler):
    def get(self):
        course = {
            'id': '1000-612BDB',
            'edition': '123123123',
            'name': 'Bazy danych w bankowosci i zarzadzaniu',
            'desciption': '1. Tekstowe bazy danych. Dokumenty el.....'
        }
        self.write(course)
