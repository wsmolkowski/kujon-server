import logging
import os

import motor
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging

import settings
from handlers.handlers_api_courses import CourseHandler
from handlers.handlers_api_courses import CoursesEditionsHandler
from handlers.handlers_api_friends import FriendsSuggestionsApi
from handlers.handlers_api_grades import GradesForCourseAndTermHandler, GradesForUserHandler
from handlers.handlers_api_terms import TermsApi, TermApi
from handlers.handlers_api_user import UserApi
from handlers.handlers_auth import CreateUserHandler
from handlers.handlers_auth import LoginHandler
from handlers.handlers_auth import LogoutHandler
from handlers.handlers_auth import VerifyHandler
from handlers.handlers_web import ChatHandler
from handlers.handlers_web import CourseInfoWebHandler
from handlers.handlers_web import CoursesWebHandler
from handlers.handlers_web import FriendsHandler
from handlers.handlers_web import FriendsSuggestionsHandler
from handlers.handlers_web import GradesWebHandler
from handlers.handlers_web import MainHandler, UserHandler
from handlers.handlers_web import SchoolHandler
from handlers.handlers_web import SettingsHandler
from handlers.handlers_web import TermsWebHandler, TermWebHandler
from mongo_utils import Dao
from usosqueue import UsosQueue


class Application(tornado.web.Application):
    _crowler = None

    @property
    def crowler(self):
        if not self._crowler:
            self._crowler = UsosQueue()
        return self._crowler


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

            (r"/user", UserHandler),

            (r"/school", SchoolHandler),
            (r"/school/grades/course/([^/]+)/([^/]+)", GradesWebHandler),
            (r"/school/courses", CoursesWebHandler),
            (r"/school/courses/([^/]+)", CourseInfoWebHandler),
            (r"/school/terms", TermsWebHandler),
            (r"/school/terms/([^/]+)", TermWebHandler),

            (r"/chat", ChatHandler),

            (r"/friends", FriendsHandler),
            (r"/friends/suggestions", FriendsSuggestionsHandler),

            (r"/settings", SettingsHandler),

            (r"/authentication/login", LoginHandler),
            (r"/authentication/logout", LogoutHandler),
            (r"/authentication/create", CreateUserHandler),
            (r"/authentication/verify", VerifyHandler),

            (r"/api/user", UserApi),
            (r"/api/courseseditions", CoursesEditionsHandler),
            (r"/api/courses/([^/]+)", CourseHandler),
            (r"/api/grades/course/([^/]+)/([^/]+)", GradesForCourseAndTermHandler),
            (r"/api/grades", GradesForUserHandler),
            (r"/api/terms", TermsApi),
            (r"/api/terms/([^/]+)", TermApi),
            (r"/api/fiends/suggestions", FriendsSuggestionsApi),

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
        self.crowler


def main():
    tornado.options.parse_command_line()
    enable_pretty_logging()

    app = Application()
    app.listen(settings.PORT)
    logging.info('http://localhost:{0}'.format(settings.PORT))
    IOLoop.instance().add_callback(app.crowler.queue_watcher)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
