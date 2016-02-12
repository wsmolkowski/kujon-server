import os

import settings
import motor
import tornado.ioloop
import tornado.web
from tornado.log import enable_pretty_logging
from tornado.options import parse_command_line

from usosweb.handlers import web, authorization


class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


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
            #(r"/static/(.*)", NoCacheStaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
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
            cookie_secret='Pl3jCVQO55nZMhxKXHNWivZpPl3jCVQO55nZMhxKXHNWivZpPl3jCVQO55nZMhxKXHNWivZp',
            google_oauth={'key': '245488701889-dfhvfuf9br6u6t9476gt0l5ngkvacota.apps.googleusercontent.com',
                          'secret': 'Pl3jCVQO55nZMhxKXHNWivZp'}

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
