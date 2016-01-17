import os
import motor
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop

import settings
from handlers_api import CoursesHandler
from handlers_api import GradesForAllCoursesAndTermsHandler
from handlers_api import GradesForCourseAndTermHandler
from handlers_api import UserHandler

from handlers_web import MainHandler
from handlers_web import LoginHandler
from handlers_web import LogoutHandler
from handlers_web import CreateUserHandler
from handlers_web import TestHandler
from mongo_utils import Dao


class Application(tornado.web.Application):

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
            (r"/test", TestHandler),
            (r"/authentication/login", LoginHandler),
            (r"/authentication/logout", LogoutHandler),
            (r"/authentication/create", CreateUserHandler),
            (r"/api/user", UserHandler),
            (r"/api/logout", LogoutHandler),
            (r"/api/courses", CoursesHandler),
            (r"/api/grades", GradesForCourseAndTermHandler),
            (r"/api/gradesall", GradesForAllCoursesAndTermsHandler),
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

        self.__prepare()

    def __prepare(self):
        self._dao.prepare()



def main():
    app = Application()
    app.listen(settings.PORT)
    print 'http://localhost:{0}'.format(settings.PORT)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
