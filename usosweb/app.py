import os

import tornado.ioloop
from tornado.log import enable_pretty_logging
from tornado.options import parse_command_line
import motor

import handlers_auth
import handlers_web


class Application(tornado.web.Application):
    _db = None
    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient('mongodb://localmongoinstance/usos-test2')
        return self._db['usos-test2']

    def __init__(self):
        __handlers = [
            (r"/", handlers_web.MainHandler),
            (r"/api/user", handlers_web.UserHandler),
            (r"/authentication/register", handlers_auth.RegisterHandler),
            (r"/authentication/login", handlers_auth.LoginHandler),
            (r"/authentication/logout", handlers_auth.LogoutHandler),
            (r"/authentication/create", handlers_auth.CreateUserHandler),
            (r"/authentication/verify", handlers_auth.VerifyHandler),
            (r"/authentication/google", handlers_auth.GoogleOAuth2LoginHandler),
        ]

        __settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            auto_reload=True,
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
    app.listen(8888)
    print 'http://localhost:8888'
    tornado.ioloop.IOLoop.current().start()
