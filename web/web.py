import os
import logging

import motor
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line

from handlers import web
from commons import settings, utils

utils.initialize_logging('web_server')


class Application(tornado.web.Application):

    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    def __init__(self):
        __handlers = [
            (r"/", web.MainHandler),
            (r"/config", web.ApplicationConfigHandler),
        ]

        __settings = dict(
            debug=settings.DEBUG,
            autoreload=settings.RELOAD,
            login_url=settings.LOGIN_URL,
            compress_response=settings.COMPRESS_RESPONSE,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=settings.COOKIE_SECRET,
            google_oauth={'key': settings.GOOGLE_CLIENT_ID, 'secret': settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': settings.FACEBOOK_CLIENT_ID, 'secret': settings.FACEBOOK_CLIENT_SECRET}
        )

        tornado.web.Application.__init__(self, __handlers, **__settings)

        self.db


if __name__ == "__main__":
    parse_command_line()

    application = Application()
    application.listen(settings.WEB_PORT, address=settings.SITE_DOMAIN)
    logging.info(settings.DEPLOY_WEB)
    tornado.ioloop.IOLoop.current().start()
