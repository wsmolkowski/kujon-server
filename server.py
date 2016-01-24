import os
import motor
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
import settings

from handlers_api_courses import CoursesEditionsHandler, CourseHandler
from handlers_api_grades import GradesForCourseAndTermHandler
from handlers_api_user import UserHandler

from handlers_auth import CreateUserHandler
from handlers_auth import LoginHandler
from handlers_auth import LogoutHandler
from handlers_auth import VerifyHandler

from handlers_web import MainHandler
from handlers_web import SchoolHandler
from handlers_web import GradesWebHandler
from handlers_web import CoursesWebHandler
from handlers_web import ChatHandler
from handlers_web import FriendsHandler
from handlers_web import SettingsHandler

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
            (r"/school", SchoolHandler),
            (r"/school/grades", GradesWebHandler),
            (r"/school/courses", CoursesWebHandler),
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

def main():
    app = Application()
    app.listen(settings.PORT)
    print 'http://localhost:{0}'.format(settings.PORT)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
