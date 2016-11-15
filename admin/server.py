# coding=utf-8

import logging
import os
import ssl

import motor
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line, define, options

from admin.handlers.base import MainHandler, DefaultErrorHandler
from admin.handlers.statistics.database import DatabaseHandler
from admin.handlers.statistics.exceptions import ExceptionsHandler
from admin.handlers.statistics.statistics import StatisticsBaseHandler
from admin.handlers.statistics.user import UsersHandler
from admin.handlers.statistics.usos import UsosHandler
from admin.handlers.statistics.usosuser import UsosUserHandler
from commons import constants
from commons.config import Config

define('environment', default='development')


def get_application(config):
    class Application(tornado.web.Application):
        def __init__(self):
            __handlers = [
                (r"/", MainHandler),
                (r"/statistics", StatisticsBaseHandler),
                (r"/statistics/users", UsersHandler),
                (r"/statistics/usos", UsosHandler),
                (r"/statistics/usosuser", UsosUserHandler),
                (r"/statistics/exceptions", ExceptionsHandler),
                (r"/statistics/database", DatabaseHandler),
            ]

            __settings = dict(
                debug=config.DEBUG,
                autoreload=config.RELOAD,
                compress_response=config.COMPRESS_RESPONSE,
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
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
        # server.bind(config.ADMIN_PORT)
        # server.start(0)  # Forks multiple sub-processes
        server.listen(config.ADMIN_PORT)
        logging.info('SSL ENABLED FOR WEB')
    else:
        server = HTTPServer(application)
        server.listen(config.ADMIN_PORT)
        logging.info('SSL DISABLED FOR WEB')

    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]
    logging.info(db)
    application.settings[constants.APPLICATION_DB] = db
    application.settings[constants.APPLICATION_CONFIG] = config
    # application.settings[constants.APPLICATION_AES] = AESCipher(config.AES_SECRET)

    logging.info(config.ADMIN_WEB)
    tornado.ioloop.IOLoop.current().start()
