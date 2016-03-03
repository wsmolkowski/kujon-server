import os
import logging

import motor
import tornado.ioloop
import tornado.web
from tornado.log import enable_pretty_logging
from tornado.options import parse_command_line

from handlers import web, authentication
from commons import settings


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
            (r"/authentication/register", authentication.RegisterHandler),
            (r"/authentication/login", authentication.LoginHandler),
            (r"/authentication/logout", authentication.LogoutHandler),
            (r"/authentication/create", authentication.CreateUserHandler),
            (r"/authentication/verify", authentication.VerifyHandler),
            (r"/authentication/google", authentication.GoogleOAuth2LoginHandler),
            (r"/authentication/facebook", authentication.FacebookOAuth2LoginHandler),
        ]

        __settings = dict(
            debug=settings.DEBUG,
            reload=settings.RELOAD,
            gzip=settings.GZIP,
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
    enable_pretty_logging()

    web = Application()
    web.listen(settings.WEB_PORT)
    logging.info(settings.DEPLOY_WEB)

    print settings.CALLBACK_URL

    tornado.ioloop.IOLoop.current().start()
