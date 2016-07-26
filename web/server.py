# coding=utf-8

import logging
import os
import ssl

import motor
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line, define, options

from commons import settings
from web.handlers import MainHandler, ContactHandler, DisclaimerHandler, DefaultErrorHandler

define("port", default=settings.WEB_PORT, help="run on the given port", type=int)
define('cookie_secret', default=settings.COOKIE_SECRET)


class Application(tornado.web.Application):

    def __init__(self):
        __handlers = [
            (r"/", MainHandler),
            (r"/contact", ContactHandler),  # post only
            (r"/regulamin", DisclaimerHandler),  # mobi and www modals content
        ]

        __settings = dict(
            debug=settings.DEBUG,
            autoreload=settings.RELOAD,
            compress_response=settings.COMPRESS_RESPONSE,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=options.cookie_secret,
            google_oauth={'key': settings.GOOGLE_CLIENT_ID, 'secret': settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': settings.FACEBOOK_CLIENT_ID, 'secret': settings.FACEBOOK_CLIENT_SECRET},
            default_handler_class=DefaultErrorHandler,
            xheaders=True,
            xsrf_cookies=True,
        )

        tornado.web.Application.__init__(self, __handlers, **__settings)


if __name__ == "__main__":
    parse_command_line()

    logging.getLogger().setLevel(settings.LOG_LEVEL)

    application = Application()

    if settings.SSL_CERT and settings.SSL_KEY:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(settings.SSL_CERT, settings.SSL_KEY)

        server = HTTPServer(application, ssl_options=ssl_ctx)
        server.bind(options.port)
        server.start(0)  # Forks multiple sub-processes
        logging.info('SSL ENABLED FOR WEB')
    else:
        server = HTTPServer(application)
        server.listen(options.port)
        logging.info('SSL DISABLED FOR WEB')

    db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]
    logging.info(db)
    application.settings['db'] = db

    logging.info(settings.DEPLOY_WEB)
    tornado.ioloop.IOLoop.current().start()