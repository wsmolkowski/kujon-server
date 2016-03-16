import tornado.gen
import tornado.web

from base import BaseHandler


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html", **self.template_data())


class ApplicationConfigHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.success(data=self.template_data())
