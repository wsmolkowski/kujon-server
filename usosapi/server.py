import logging

import motor
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
from tornado.options import define, options, parse_command_line

import settings
from handlers_list import HANDLERS
from usosutils.usosqueue import UsosQueue

define('debug', default=settings.DEBUG)
# define('port', default=settings.PORT)
define('ssl', default=settings.SSL)
define('xsrf_cookie', default=settings.XSRF_COOKIE)
define('cookie_secret', default=settings.COOKIE_SECRET)
define('autoreload', default=settings.AUTORELOAD_ENABLED)


class Application(tornado.web.Application):
    _crowler = None

    @property
    def crowler(self):
        if not self._crowler:
            self._crowler = UsosQueue()
        return self._crowler

    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    def __init__(self):

        _settings = dict(
            debug=options.debug,
            ssl=options.ssl,
            xsrf_cookies=options.xsrf_cookie,
            cookie_secret=options.cookie_secret,
            login_url=settings.LOGIN_URL,
            path=settings.ROOT_PATH,
            static_path=settings.STATIC_PATH,
            site_url=settings.DEPLOY_URL,
            site_title=settings.PROJECT_TITLE,
            site_description=settings.PROJECT_DESCRIPTION,
            site_domain=settings.SITE_DOMAIN,
            site_root=settings.SITE_ROOT,
            template_path=settings.TEMPLATES_PATH,
            gzip=settings.GZIP
        )

        tornado.web.Application.__init__(self, HANDLERS, **_settings)

        self.db
        self.crowler


def prepare_environment():
    from usosapi.usosutils.usoscrowler import UsosCrowler

    uc = UsosCrowler()
    if settings.CLEAN_DB:
        uc.drop_collections()
    if settings.UPDATE_DICTIONARIES:
        uc.recreate_usos()
        uc.recreate_dictionaries()


def main():
    parse_command_line()
    enable_pretty_logging()

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(u"DEBUG MODE is ON")

    prepare_environment()

    application = Application()
    application.listen(settings.PORT)
    logging.info(settings.DEPLOY_URL)

    IOLoop.instance().add_callback(application.crowler.queue_watcher)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
