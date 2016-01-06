import tornado.web
from datetime import date
import settings


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        config = {
            'version': settings.VERSION,
            'last_build':  date.today().isoformat()
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