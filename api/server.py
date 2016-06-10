# coding=UTF-8

import logging
import ssl

import motor
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options

from api.handlers.base import DefaultErrorHandler
from api.handlers_list import HANDLERS
from commons import settings

define("port", default=settings.API_PORT, help="run on the given port", type=int)
define('cookie_secret', default=settings.COOKIE_SECRET)


class Application(tornado.web.Application):

    def __init__(self):
        _settings = dict(
            debug=settings.DEBUG,
            autoreload=settings.RELOAD,
            compress_response=settings.COMPRESS_RESPONSE,
            cookie_secret=options.cookie_secret,
            google_oauth={'key': settings.GOOGLE_CLIENT_ID, 'secret': settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': settings.FACEBOOK_CLIENT_ID, 'secret': settings.FACEBOOK_CLIENT_SECRET},
            default_handler_class=DefaultErrorHandler,
            xheaders=True,
        )

        tornado.web.Application.__init__(self, HANDLERS, **_settings)


def main():
    parse_command_line()
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    application = Application()
    if settings.SSL_CERT and settings.SSL_KEY:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(settings.SSL_CERT, settings.SSL_KEY)

        server = HTTPServer(application, ssl_options=ssl_ctx)
        server.bind(options.port)
        server.start(0)  # Forks multiple sub-processes
        logging.info('SSL ENABLED FOR API on port: {0}'.format(options.port))
    else:
        server = HTTPServer(application)
        server.listen(options.port)
        logging.info('SSL DISABLED FOR API on port: {0}'.format(options.port))

    db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]
    logging.info(db)
    application.settings['db'] = db
    logging.info(settings.DEPLOY_API)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
