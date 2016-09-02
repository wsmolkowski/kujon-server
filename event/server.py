# coding=UTF-8

import logging
import ssl

import motor
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line, define, options

from commons import constants
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.handlers import DefaultErrorHandler
from event.handlers import EventHandler

define('environment', default='development')


def get_application(config):
    class Application(tornado.web.Application):
        def __init__(self):
            __handlers = [
                (r"/([^/]+)", EventHandler),
            ]

            __settings = dict(
                debug=config.DEBUG,
                autoreload=config.RELOAD,
                compress_response=config.COMPRESS_RESPONSE,
                default_handler_class=DefaultErrorHandler,
                xheaders=True,
            )

            tornado.web.Application.__init__(self, __handlers, **__settings)

    return Application()


def main():
    parse_command_line()

    config = Config(options.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)

    application = get_application(config)

    if config.SSL_CERT and config.SSL_KEY:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(config.SSL_CERT, config.SSL_KEY)

        server = HTTPServer(application, ssl_options=ssl_ctx)
        server.bind(config.EVENT_PORT)
        server.start(0)  # Forks multiple sub-processes
        logging.info('SSL ENABLED FOR EVENT on port: {0}'.format(config.EVENT_PORT))
    else:
        server = HTTPServer(application)
        server.listen(config.EVENT_PORT)
        logging.info('SSL DISABLED FOR EVENT on port: {0}'.format(config.EVENT_PORT))

    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]
    logging.info(db)
    application.settings[constants.APPLICATION_DB] = db
    application.settings[constants.APPLICATION_CONFIG] = config
    application.settings[constants.APPLICATION_AES] = AESCipher(config.AES_SECRET)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
