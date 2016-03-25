import logging
import sys

import motor
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options

from commons import settings, constants
from handlers.base import DefaultErrorHandler
from handlers_list import HANDLERS

define("port", default=settings.API_PORT, help="run on the given port", type=int)
define('cookie_secret', default=settings.COOKIE_SECRET)


class Application(tornado.web.Application):
    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    def __init__(self):
        _settings = dict(
            debug=settings.DEBUG,
            autoreload=settings.RELOAD,
            login_url=settings.LOGIN_URL,
            compress_response=settings.COMPRESS_RESPONSE,
            cookie_secret=options.cookie_secret,
            google_oauth={'key': settings.GOOGLE_CLIENT_ID, 'secret': settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': settings.FACEBOOK_CLIENT_ID, 'secret': settings.FACEBOOK_CLIENT_SECRET},
            default_handler_class=DefaultErrorHandler,
            xheaders=True,
        )

        tornado.web.Application.__init__(self, HANDLERS, **_settings)

        self.db


def prepare_environment():
    # change encoding to utf-8
    reload(sys)  # Reload does the trick!
    sys.setdefaultencoding(constants.ENCODING)
    if sys.getdefaultencoding() != constants.ENCODING:
        logging.error("Could not change encoding to %s".format(constants.ENCODING))


def main():
    parse_command_line()
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    prepare_environment()

    application = Application()
    application.listen(options.port)
    logging.info(settings.DEPLOY_API)

    IOLoop.instance().start()


if __name__ == "__main__":
    main()
