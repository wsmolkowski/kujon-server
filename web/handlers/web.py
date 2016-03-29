import tornado.gen
import tornado.web

from base import BaseHandler


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_cookie(con)
        self.render("index.html", **self.config_data())

