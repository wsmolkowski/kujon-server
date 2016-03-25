import logging
import os

import motor
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line, define, options

from commons import settings
from handlers import web
from handlers.base import DefaultErrorHandler

define("port", default=settings.WEB_PORT, help="run on the given port", type=int)
define('cookie_secret', default=settings.COOKIE_SECRET)


class Application(tornado.web.Application):

    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    def __init__(self):
        __handlers = [
            (r"/", web.MainHandler),
            (r"/config", web.ApplicationConfigHandler),
        ]

        __settings = dict(
            debug=settings.DEBUG,
            autoreload=settings.RELOAD,
            login_url=settings.LOGIN_URL,
            compress_response=settings.COMPRESS_RESPONSE,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=options.cookie_secret,
            google_oauth={'key': settings.GOOGLE_CLIENT_ID, 'secret': settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': settings.FACEBOOK_CLIENT_ID, 'secret': settings.FACEBOOK_CLIENT_SECRET},
            default_handler_class=DefaultErrorHandler,
            xheaders=True,
        )

        tornado.web.Application.__init__(self, __handlers, **__settings)

        self.db


if __name__ == "__main__":
    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    application = Application()
    application.listen(options.port)
    logging.info(settings.DEPLOY_WEB)
    tornado.ioloop.IOLoop.current().start()
