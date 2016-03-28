import tornado.gen
import tornado.web

from base import BaseHandler


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html", **self.template_data())

