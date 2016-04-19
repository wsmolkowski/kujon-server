import tornado.gen
import tornado.web
from bson import json_util
from tornado.web import RequestHandler

from commons import constants, settings
from commons.mixins.JSendMixin import JSendMixin

CONFIG_COOKIE_EXPIRATION = 1

CONFIG = {
    'PROJECT_TITLE': settings.PROJECT_TITLE,
    'KUJON_SECURE_COOKIE': constants.KUJON_SECURE_COOKIE,
    'API_URL': settings.DEPLOY_API,
    'WEB_VERSION': settings.WEB_VERSION,
}


class MainHandler(RequestHandler, JSendMixin):
    @tornado.web.asynchronous
    def get(self):
        self.set_cookie(constants.KUJON_CONFIG_COOKIE,
                        tornado.escape.url_escape(json_util.dumps(CONFIG)),
                        expires_days=CONFIG_COOKIE_EXPIRATION)
        self.render("index.html", **CONFIG)


class DefaultErrorHandler(RequestHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = CONFIG
        data['MESSAGE'] = '404 - Strona o podanym adresie nie istnieje.'
        self.render('error.html', **data)
