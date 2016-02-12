import tornado.gen
import tornado.web

from base import BaseHandler
from usosweb import settings


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html", **self.template_data())


class ApplicationConfigHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        config = {
            'USOS_API': settings.USOS_API
        }
        self.set_header("Content-Type", "application/json")
        self.write_json(data=config)