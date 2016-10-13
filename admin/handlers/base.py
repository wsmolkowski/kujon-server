# coding=UTF-8

import logging

from tornado import web

from admin.handlers import constants as admin_constants
from commons import constants


class BaseHandler(web.RequestHandler):
    SUPPORTED_METHODS = ('GET',)

    @property
    def db(self):
        return self.application.settings[constants.APPLICATION_DB]

    @property
    def config(self):
        return self.application.settings[constants.APPLICATION_CONFIG]

    @property
    def aes(self):
        return self.application.settings[constants.APPLICATION_AES]

    def _base_config(self):
        return dict(PROJECT_TITLE=self.config.PROJECT_TITLE, DEPLOY_WEB=self.config.DEPLOY_WEB)

    def _render_page(self, template, data=None):
        if not data:
            data = self._base_config()
        else:
            data.update(self._base_config())

        logging.debug(data)
        self.render(template, **data)

    def _render_error(self, data):
        logging.exception(data)

        if isinstance(data, Exception):
            data = {admin_constants.TEMPLATE_MESSAGE: str(data)}

        self._render_page("error.html", data)


class MainHandler(BaseHandler):
    @web.removeslash
    @web.asynchronous
    def get(self):
        self._render_page("index.html")


class DefaultErrorHandler(BaseHandler):
    @web.asynchronous
    def get(self):
        self._render_error(
            {admin_constants.TEMPLATE_MESSAGE:
                 "Spróbuj kliknąć w innym miejsu, bądź napisz do nas jeśli spodziewałeś się strony pod tym adresem."})
