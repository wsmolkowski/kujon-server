import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop

import settings
from handlers import ClassGroup
from handlers import MainHandler
from handlers import ScheduleHandler
from handlers import SchoolHandler
from handlers import UserHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", MainHandler),
            (r"/api/school/([0-9])+", SchoolHandler),
            (r"/api/user/id/([0-9]+)", UserHandler),
            (r"/api/schedule/user_id/([0-9])+/startdate/([0-9])+", ScheduleHandler),
            (r"/api/classgroup/([0-9])+", ClassGroup),

        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(settings.PORT)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()

