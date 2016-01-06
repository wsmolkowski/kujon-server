import tornado.web
from datetime import date
import settings
import json


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        config = {
            'version': settings.VERSION,
            'last_build': date.today().isoformat()
        }

        self.write(config)


class SchoolHandler(tornado.web.RequestHandler):
    def get(self, school_id):
        school = {
            'school_id': school_id,
            'type': 0,
            'version': 1
        }

        self.write(school)




class Contacts():
    contacts = {}



class UserHandler(tornado.web.RequestHandler):
    user_id = 0
    phone = "022000000"
    email = "email"
    avatar = "zdjecie"
    name = "imie i nazwisko"

    # school = School()
    contacts = Contacts()
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
