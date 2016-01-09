import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
import motor


import settings

from handlers import ClassGroupHandler
from handlers import MainHandler
from handlers import CoursesHandler
from handlers import UserHandler


class Application(tornado.web.Application):

    _db_connection = None
    @property
    def db(self):
        if not self._db_connection:
            self._db_connection = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db_connection[settings.MONGODB_NAME]

    def __init__(self):

        handlers = [
            (r"/?", MainHandler),
            (r"/api/user?", UserHandler),
            (r"/api/Courses", CoursesHandler),
            (r"/api/classgroup/([0-9])+", ClassGroupHandler),

        ]

        tornado.web.Application.__init__(self, handlers)

        self.db


def main():
    app = Application()
    app.listen(settings.PORT)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
