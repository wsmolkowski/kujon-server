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
from commons.config import Config

define('environment', default='development')


def get_application(config):
    class Application(tornado.web.Application):
        def __init__(self):
            _settings = dict(
                debug=config.DEBUG,
                autoreload=config.RELOAD,
                compress_response=config.COMPRESS_RESPONSE,
                cookie_secret=config.COOKIE_SECRET,
                google_oauth={'key': config.GOOGLE_CLIENT_ID, 'secret': config.GOOGLE_CLIENT_SECRET},
                facebook_oauth={'key': config.FACEBOOK_CLIENT_ID, 'secret': config.FACEBOOK_CLIENT_SECRET},
                default_handler_class=DefaultErrorHandler,
                xheaders=True,
            )

            tornado.web.Application.__init__(self, HANDLERS, **_settings)

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
        server.bind(config.API_PORT)
        server.start(0)  # Forks multiple sub-processes
        logging.info('SSL ENABLED FOR API on port: {0}'.format(config.API_PORT))
    else:
        server = HTTPServer(application)
        server.listen(config.API_PORT)
        logging.info('SSL DISABLED FOR API on port: {0}'.format(config.API_PORT))

    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]
    logging.info(db)
    application.settings['db'] = db
    application.settings['config'] = config
    logging.info(config.DEPLOY_API)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
