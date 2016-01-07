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

'''
class Contacts(json.JSONEncoder):
    contacts = {}
    name = ""

    def __init__(self, name):
        self.name = name

    def to_json(self):  # New special method.
        return "{u'name': %r}" % self.name.decode('utf-8')

    def default(self, o):
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, o)
'''

class UserHandler(tornado.web.RequestHandler):
    user_id = 0
    phone = "022000000"
    email = "email"
    avatar = "zdjecie"
    name = "imie i nazwisko"

    # school = School()
    # contacts = Contacts("Dupek aaa")
    # contactsLocked = ContactsLocked()

    # dane do outh do podlaczenia do usosa
    # do przemyslenia czy tutaj.
    # Consumer Key to use.
    consumer_key = 'KBt6uWPWUekUzFtNTyY9';
    consumer_secret = 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG';

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
    def get(self, user_id, start_date, schedule_period=settings.DEFAULT_SCHEDULE_PERIOD):

        start_date = datetime.strptime(start_date, settings.DATE_FORMAT)
        end_date = start_date + datetime.timedelta(days=schedule_period)

        schedule = {
            '2016-01-04': {
                '1238': {
                    'start_time': '07:00',
                    'end_time': '09:00',
                    'type': 'egzamin',
                    'place': '5959'
                },
                '1238': {
                    'start_time': '07:00',
                    'end_time': '09:00',
                    'type': 'egzamin',
                    'place': '8173'
                }

            },
            '2016-01-05': {
                'group_id': 1231,
                'start_time': '09:00',
                'end_time': '10:00',
                'type': 'lab'
            }
        }
        self.write(schedule)

class ClassGroup(tornado.web.RequestHandler):

    def get(self, user_id,classgroupid):
        classGroup = {
                'classGroupId': classgroupid,
                'start_time': '07:00',
                'end_time': '09:00',
                'type': 'egzamin',
                'place': '5959',
                'teacher': 'Jan Kiepura',
                'ocures': 'co tydzien'
         }
        self.write(classGroup)

