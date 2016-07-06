# coding=UTF-8

import logging
import ssl

import motor
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line, define, options

from commons import settings
from handlers import EventHandler, DefaultErrorHandler

define("port", default=settings.EVENT_PORT, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        __handlers = [
            (r"/", EventHandler),
        ]

        __settings = dict(
            debug=settings.DEBUG,
            autoreload=settings.RELOAD,
            compress_response=settings.COMPRESS_RESPONSE,
            default_handler_class=DefaultErrorHandler,
            xheaders=True,
        )

        tornado.web.Application.__init__(self, __handlers, **__settings)


def main():
    parse_command_line()

    logging.getLogger().setLevel(settings.LOG_LEVEL)

    application = Application()

    if settings.SSL_CERT and settings.SSL_KEY:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(settings.SSL_CERT, settings.SSL_KEY)

        server = HTTPServer(application, ssl_options=ssl_ctx)
        server.bind(options.port)
        server.start(0)  # Forks multiple sub-processes
        logging.info('SSL ENABLED FOR EVENT on port: {0}'.format(options.port))
    else:
        server = HTTPServer(application)
        server.listen(options.port)
        logging.info('SSL DISABLED FOR EVENT on port: {0}'.format(options.port))

    db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]
    logging.info(db)
    application.settings['db'] = db
    logging.info(settings.DEPLOY_EVENT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
