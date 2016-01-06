import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop

import settings
from handlers import MainHandler
from handlers import ConfigHandler
from handlers import SchoolHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", MainHandler),
            (r"/config", ConfigHandler),
            (r"/api/school/([0-9])+", SchoolHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(settings.PORT)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()

