# coding=utf-8

import logging
import os
import ssl

import motor
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line, define, options

from commons import constants
from commons.AESCipher import AESCipher
from commons.config import Config
from web.handlers import MainHandler, ContactHandler, DisclaimerHandler, DefaultErrorHandler

define('environment', default='development')


def get_application(config):
    class Application(tornado.web.Application):
        def __init__(self):
            __handlers = [
                (r"/", MainHandler),
                (r"/contact", ContactHandler),  # post only
                (r"/regulamin", DisclaimerHandler),  # mobi and www modals content
            ]

            __settings = dict(
                debug=config.DEBUG,
                autoreload=config.RELOAD,
                compress_response=config.COMPRESS_RESPONSE,
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                cookie_secret=config.COOKIE_SECRET,
                google_oauth={'key': config.GOOGLE_CLIENT_ID, 'secret': config.GOOGLE_CLIENT_SECRET},
                facebook_oauth={'key': config.FACEBOOK_CLIENT_ID, 'secret': config.FACEBOOK_CLIENT_SECRET},
                default_handler_class=DefaultErrorHandler,
                xheaders=True,
                xsrf_cookies=True,
            )

            tornado.web.Application.__init__(self, __handlers, **__settings)

    return Application()


if __name__ == "__main__":
    parse_command_line()
    config = Config(options.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)

    application = get_application(config)

    if config.SSL_CERT and config.SSL_KEY:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(config.SSL_CERT, config.SSL_KEY)

        server = HTTPServer(application, ssl_options=ssl_ctx)
        server.bind(config.WEB_PORT)
        server.start(0)  # Forks multiple sub-processes
        logging.info('SSL ENABLED FOR WEB')
    else:
        server = HTTPServer(application)
        server.listen(config.WEB_PORT)
        logging.info('SSL DISABLED FOR WEB')

    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]
    logging.info(db)
    application.settings[constants.APPLICATION_DB] = db
    application.settings[constants.APPLICATION_CONFIG] = config
    application.settings[constants.APPLICATION_AES] = AESCipher(config.AES_SECRET)

    logging.info(config.DEPLOY_WEB)
    tornado.ioloop.IOLoop.current().start()
