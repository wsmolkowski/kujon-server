import os

import settings
import motor
import tornado.ioloop
import tornado.web
from tornado.log import enable_pretty_logging
from tornado.options import parse_command_line

from staraweb.handlers import web, authorization
from staracommon import settings as common_settings


class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


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
            #(r"/static/(.*)", NoCacheStaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
            (r"/config", web.ApplicationConfigHandler),
            (r"/authentication/register", authorization.RegisterHandler),
            (r"/authentication/login", authorization.LoginHandler),
            (r"/authentication/logout", authorization.LogoutHandler),
            (r"/authentication/create", authorization.CreateUserHandler),
            (r"/authentication/verify", authorization.VerifyHandler),
            (r"/authentication/google", authorization.GoogleOAuth2LoginHandler),
        ]

        __settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=common_settings.COOKIE_SECRET,
            google_oauth={'key': common_settings.GOOGLE_CLIENT_ID, 'secret': common_settings.GOOGLE_CLIENT_SECRET}
        )

        tornado.web.Application.__init__(self, __handlers, **__settings)

        self.db


if __name__ == "__main__":
    parse_command_line()
    enable_pretty_logging()

    app = Application()
    app.listen(settings.PORT)
    print settings.DEPLOY_URL
    tornado.ioloop.IOLoop.current().start()
