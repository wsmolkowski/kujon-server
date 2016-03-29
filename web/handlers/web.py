import tornado.gen
import tornado.web
from bson import json_util

from base import BaseHandler
from commons import constants

CONFIG_COOKIE_EXPIRATION = 1


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_cookie(constants.KUJON_CONFIG_COOKIE,
                        tornado.escape.url_escape(json_util.dumps(self.config_data())),
                        expires_days=CONFIG_COOKIE_EXPIRATION)
        self.render("index.html", **self.config_data())

