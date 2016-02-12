import tornado.gen
import tornado.web

from base import BaseHandler
from usosweb import settings


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html", **self.template_data())


class UserHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()

        user = yield self.db.users.find_one(user['_id'],
                                            ('family_name', 'given_name', 'locale', 'user_type', 'email', 'picture'))
        user.pop('_id')

        self.write_json(data=user)


class ApplicationConfigHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        config = {
            'USOS_API': settings.USOS_API
        }
        self.write_json(data=config)