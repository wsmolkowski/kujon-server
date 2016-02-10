import tornado.gen
import tornado.web
from bson import json_util


class BaseHandler(tornado.web.RequestHandler):
    USER_SECURE_COOKIE = 'USER_SECURE_COOKIE'

    def get_current_user(self):
        cookie = self.get_secure_cookie(self.USER_SECURE_COOKIE)
        if cookie:
            cookie = tornado.escape.json_decode(cookie)
            return json_util.loads(cookie)
        return None

    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

    @property
    def db(self):
        return self.application.db


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")


class UserHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()

        user = yield self.db.users.find_one(user['_id'],
                                            ('family_name', 'given_name', 'locale', 'user_type', 'email', 'picture'))
        user.pop('_id')
        self.set_header("Content-Type", "application/json")
        self.write(json_util.dumps(user))
