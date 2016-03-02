import os

import settings
import motor
import tornado.ioloop
import tornado.web
from tornado.log import enable_pretty_logging
from tornado.options import parse_command_line

from handlers import web, authentication
from commons import settings as common_settings


class Application(tornado.web.Application):

    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(common_settings.MONGODB_URI)
        return self._db[common_settings.MONGODB_NAME]

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
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=common_settings.COOKIE_SECRET,
            google_oauth={'key': common_settings.GOOGLE_CLIENT_ID, 'secret': common_settings.GOOGLE_CLIENT_SECRET},
            facebook_oauth={'key': common_settings.FACEBOOK_CLIENT_ID, 'secret': common_settings.FACEBOOK_CLIENT_SECRET}
        )

        tornado.web.Application.__init__(self, __handlers, **__settings)

        self.db


if __name__ == "__main__":
    parse_command_line()
    enable_pretty_logging()

    web = Application()
    web.listen(settings.PORT)
    print settings.DEPLOY_URL
    tornado.ioloop.IOLoop.current().start()
