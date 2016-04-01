import tornado.gen
import tornado.web
from bson import json_util

from commons.mixins.JSendMixin import JSendMixin
from commons.handlers import CommonHandler
from commons import constants

CONFIG_COOKIE_EXPIRATION = 1


class MainHandler(CommonHandler, JSendMixin):
    @tornado.web.asynchronous
    def get(self):
        self.set_cookie(constants.KUJON_CONFIG_COOKIE,
                        tornado.escape.url_escape(json_util.dumps(self.config_data())),
                        expires_days=CONFIG_COOKIE_EXPIRATION)
        self.render("index.html", **self.config_data())


class DefaultErrorHandler(CommonHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        data['message'] = 'Przepraszamy ale strona o podanym adresie nie istnieje.'
        self.render('error.html', **data)
