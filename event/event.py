# coding=UTF-8

import logging
import ssl

import motor
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line, define, options

from commons import settings
from handlers import EventHandler, VerifyHandler, DefaultErrorHandler

define("port", default=settings.EVENT_PORT, help="run on the given port", type=int)


class Application(tornado.web.Application):
    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    def __init__(self):
        __handlers = [
            (r"/", EventHandler),
            (r"/verify", VerifyHandler),
        ]

        __settings = dict(
            debug=settings.DEBUG,
            autoreload=settings.RELOAD,
            compress_response=settings.COMPRESS_RESPONSE,
            default_handler_class=DefaultErrorHandler,
            xheaders=True,
        )

        tornado.web.Application.__init__(self, __handlers, **__settings)

        logging.debug(self.db)


if __name__ == "__main__":
    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    application = Application()

    if settings.SSL_CERT and settings.SSL_KEY:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(settings.SSL_CERT, settings.SSL_KEY)

        server = HTTPServer(application, ssl_options=ssl_ctx)
        server.listen(options.port)
        logging.info('SSL ENABLED FOR EVENT')
    else:
        application.listen(options.port)
        logging.info('SSL DISABLED FOR EVENT')

    logging.info(settings.DEPLOY_EVENT)
    tornado.ioloop.IOLoop.current().start()
