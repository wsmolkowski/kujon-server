import json
from datetime import datetime

import tornado.web

import settings


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
    user_id = 0
    phone = "022000000"
    email = "email"
    avatar = "zdjecie"
    name = "imie i nazwisko"

    # school = School()
    #contacts = Contacts("Dupek aaa")
    # contactsLocked = ContactsLocked()

    # dane do outh do podlaczenia do usosa
    # do przemyslenia czy tutaj.

    # Access Token to use. If left blank, then user authorization process will follow.
    access_token_key = '3ShYQv8LyvgeXthKJzmJ'
    access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'

    def get(self, user_id):

        user = {
            'school_id': user_id,
            'phone': self.phone,
            'email': self.email,
            'avatar': self.avatar,
            'name': self.name,
            'contacts': self.contacts,
            # 'school': self.school,
            # 'contactsLocked': self.contactsLocked
        }
        self.write(user)

    def post(self, *args, **kwargs):
        print args


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
            'teacher': 'Jan Kiepura',
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
