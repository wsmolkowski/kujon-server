import logging
import sys

import motor
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
from tornado.options import define, options, parse_command_line

import settings
from handlers_list import HANDLERS
from staracommon import settings as common_settings

define('debug', default=settings.DEBUG)
define('port', default=settings.PORT)
define('ssl', default=settings.SSL)
define('cookie_secret', default=common_settings.COOKIE_SECRET)


class Application(tornado.web.Application):
    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(common_settings.MONGODB_URI)
        return self._db[common_settings.MONGODB_NAME]

    def __init__(self):

        _settings = dict(
            debug=options.debug,
            ssl=options.ssl,
            cookie_secret=options.cookie_secret,
            site_url=settings.DEPLOY_URL,
            site_domain=settings.SITE_DOMAIN,
            site_root=settings.SITE_ROOT,
            gzip=settings.GZIP,
            google_oauth={'key': common_settings.GOOGLE_CLIENT_ID, 'secret': common_settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': common_settings.FACEBOOK_CLIENT_ID, 'secret': common_settings.FACEBOOK_CLIENT_SECRET}
        )

        tornado.web.Application.__init__(self, HANDLERS, **_settings)

        self.db


def prepare_environment():
    from staracommon.usosutils.usoscrowler import UsosCrowler

    uc = UsosCrowler()
    if settings.CLEAN_DB:
        try:
            uc.drop_collections()
            uc.recreate_usos()
            uc.recreate_dictionaries()
        except Exception, ex:
            logging.error("Problem during preparation env:".format(ex.message))
            SystemExit()


def main():
    parse_command_line()
    enable_pretty_logging()

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(u"DEBUG MODE is ON")

    # change encoding to utf-8
    reload(sys)  # Reload does the trick!
    sys.setdefaultencoding('utf-8')
    if sys.getdefaultencoding()!='utf-8':
        logging.error(u"zmien kodowanie na UTF8!")

    prepare_environment()

    application = Application()
    application.listen(options.port)
    logging.info(settings.DEPLOY_URL)

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
