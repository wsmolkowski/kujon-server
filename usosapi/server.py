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
from handlers.handlers_api_courses import CoursesEditionsApi
from handlers.handlers_api_friends import FriendsSuggestionsApi
from handlers.handlers_api_grades import GradesForCourseAndTermApi, GradesForUserApi
from handlers.handlers_api_terms import TermsApi, TermApi
from handlers.handlers_api_user import UserApi
from handlers.handlers_auth import CreateUserHandler
from handlers.handlers_auth import LoginHandler
from handlers.handlers_auth import LogoutHandler
from handlers.handlers_auth import VerifyHandler
from handlers.handlers_chat import ChatHandler, ChatSocketHandler
from handlers.handlers_web import CourseInfoWebHandler
from handlers.handlers_web import CoursesWebHandler
from handlers.handlers_web import FriendsHandler
from handlers.handlers_web import FriendsSuggestionsHandler
from handlers.handlers_web import GradesWebHandler
from handlers.handlers_web import MainHandler, UserHandler
from handlers.handlers_web import SchoolHandler
from handlers.handlers_web import SettingsHandler
from handlers.handlers_web import TermsWebHandler, TermWebHandler
from usosqueue import UsosQueue


class Application(tornado.web.Application):
    _crowler = None

    @property
    def crowler(self):
        if not self._crowler:
            self._crowler = UsosQueue()
        return self._crowler

    _db_connection = None

    @property
    def db(self):
        if not self._db_connection:
            self._db_connection = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db_connection[settings.MONGODB_NAME]

    def __init__(self):

        handlers = [
            (r"/?", MainHandler),

            (r"/user", UserHandler),

            (r"/school", SchoolHandler),
            (r"/school/grades", SchoolHandler),
            (r"/school/grades/course/([^/]+)/([^/]+)", GradesWebHandler),
            (r"/school/courses", CoursesWebHandler),
            (r"/school/courses/([^/]+)", CourseInfoWebHandler),
            (r"/school/terms", TermsWebHandler),
            (r"/school/terms/([^/]+)", TermWebHandler),

            (r"/chat", ChatHandler),
            (r"/chatsocket", ChatSocketHandler),


            (r"/friends", FriendsHandler),
            (r"/friends/suggestions", FriendsSuggestionsHandler),

            (r"/settings", SettingsHandler),

            (r"/authentication/login", LoginHandler),
            (r"/authentication/logout", LogoutHandler),
            (r"/authentication/create", CreateUserHandler),
            (r"/authentication/verify", VerifyHandler),

            (r"/api/user", UserApi),

            (r"/api/courseseditions", CoursesEditionsApi),
            (r"/api/courses/([^/]+)", CourseHandler),

            (r"/api/grades/course/([^/]+)/([^/]+)", GradesForCourseAndTermApi),
            (r"/api/grades", GradesForUserApi),

            (r"/api/terms", TermsApi),
            (r"/api/terms/([^/]+)", TermApi),

            (r"/api/friends/suggestions", FriendsSuggestionsApi),
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
        self.crowler


def prepare_environment():
    from usoscrowler import UsosCrowler

    uc = UsosCrowler()
    uc.prepare_database()
    uc.recreate_dictionaries()


def main():
    tornado.options.parse_command_line()
    enable_pretty_logging()

    prepare_environment()

    app = Application()
    app.listen(settings.PORT)
    logging.info('http://localhost:{0}'.format(settings.PORT))
    IOLoop.instance().add_callback(app.crowler.queue_watcher)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
