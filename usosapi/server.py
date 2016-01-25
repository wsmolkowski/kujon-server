import os
import logging

import motor
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.log import enable_pretty_logging

from handlers.handlers_api_courses import CoursesEditionsHandler
from handlers.handlers_api_courses import CourseHandler
from handlers.handlers_api_grades import GradesForCourseAndTermHandler
from handlers.handlers_api_user import UserHandler
from handlers.handlers_auth import CreateUserHandler
from handlers.handlers_auth import LoginHandler
from handlers.handlers_auth import LogoutHandler
from handlers.handlers_auth import VerifyHandler
from handlers.handlers_web import ChatHandler
from handlers.handlers_web import CoursesWebHandler
from handlers.handlers_web import FriendsHandler
from handlers.handlers_web import GradesWebHandler
from handlers.handlers_web import MainHandler
from handlers.handlers_web import SchoolHandler
from handlers.handlers_web import SettingsHandler
from handlers.handlers_web import CoursesInfoWebHandler
from tornado.ioloop import IOLoop

import settings
from mongo_utils import Dao


tornado.options.parse_command_line()
enable_pretty_logging()


class Application(tornado.web.Application):
    _usoses = None
    @property
    def usoses(self):
        if not self._usoses:
            self._usoses = list(self.dao.get_usoses())
        return self._usoses

    _db_connection = None
    @property
    def db(self):
        if not self._db_connection:
            self._db_connection = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db_connection[settings.MONGODB_NAME]

    _dao = None
    @property
    def dao(self):
        if not self._dao:
            self._dao = Dao()
        return self._dao

    def __init__(self):

        handlers = [
            (r"/?", MainHandler),
            (r"/school", SchoolHandler),
            (r"/school/grades", GradesWebHandler),
            (r"/school/courses", CoursesWebHandler),
            (r"/school/courses/([^/]+)", CoursesInfoWebHandler),
            (r"/chat", ChatHandler),
            (r"/friends", FriendsHandler),
            (r"/settings", SettingsHandler),
            (r"/authentication/login", LoginHandler),
            (r"/authentication/logout", LogoutHandler),
            (r"/authentication/create", CreateUserHandler),
            (r"/authentication/verify", VerifyHandler),

            (r"/api/user", UserHandler),
            (r"/api/courseseditions", CoursesEditionsHandler),
            (r"/api/courses/(.*)", CourseHandler),
            (r"/api/grades", GradesForCourseAndTermHandler),

        ]

        app_settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            "login_url": "/authentication/login",
            "xsrf_cookies": True,
        }

        tornado.web.Application.__init__(self, handlers, **app_settings)

        self.db
        self.dao
        self.dao.prepare()
        self.usoses


def main():

    app = Application()
    app.listen(settings.PORT)
    logging.info('http://localhost:{0}'.format(settings.PORT))
    IOLoop.instance().start()


if __name__ == "__main__":

    main()
