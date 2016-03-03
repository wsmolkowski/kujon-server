import logging
import sys

import motor
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
from tornado.options import define, options, parse_command_line

from commons import settings
from commons import constants
from handlers_list import HANDLERS


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
            reload=settings.RELOAD,
            gzip=settings.GZIP,
            cookie_secret=settings.COOKIE_SECRET,
            google_oauth={'key': settings.GOOGLE_CLIENT_ID, 'secret': settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': settings.FACEBOOK_CLIENT_ID, 'secret': settings.FACEBOOK_CLIENT_SECRET}
        )

        tornado.web.Application.__init__(self, HANDLERS, **_settings)

        self.db


def prepare_environment():
    # change encoding to utf-8
    reload(sys)  # Reload does the trick!
    sys.setdefaultencoding(constants.ENCODING)
    if sys.getdefaultencoding() != constants.ENCODING:
        logging.error(u"Could not change encoding to %s".format(constants.ENCODING))

    from commons.usosutils.usoscrowler import UsosCrowler

    uc = UsosCrowler()
    if settings.CLEAN_DB:
        try:
            uc.drop_collections()
            uc.recreate_usos()
            uc.recreate_dictionaries()
        except Exception, ex:
            logging.exception(u"Problem during environment preparation: %s".format(ex.message))
            sys.exit(-1)


def main():
    parse_command_line()
    enable_pretty_logging()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(u"DEBUG MODE is ON")

    prepare_environment()

    application = Application()
    application.listen(settings.API_PORT)
    logging.info(settings.DEPLOY_API)

    IOLoop.instance().start()


if __name__ == "__main__":
    main()
