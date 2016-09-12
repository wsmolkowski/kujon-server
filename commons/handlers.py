# coding=UTF-8

from tornado import web

from commons import constants
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.JSendMixin import JSendMixin


class AbstractHandler(web.RequestHandler, JSendMixin, DaoMixin):
    @property
    def db(self):
        return self.application.settings[constants.APPLICATION_DB]

    @property
    def config(self):
        return self.application.settings[constants.APPLICATION_CONFIG]

    @property
    def aes(self):
        return self.application.settings[constants.APPLICATION_AES]

    def get_remote_ip(self):
        return self.request.headers.get('X-Forwarded-For',
                                        self.request.headers.get('X-Real-Ip', self.request.remote_ip))

    def getUsosId(self):
        if hasattr(self, 'usos_id'):
            return self.usos_id

        if self.get_current_usos() and constants.USOS_ID in self.get_current_usos():
            return self.get_current_usos()[constants.USOS_ID]

        return

    async def get_usoses(self):
        usoses = []
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
        async for usos in cursor:
            usos['logo'] = self.config.DEPLOY_WEB + usos['logo']
            usoses.append(usos)

        return usoses


class DefaultErrorHandler(AbstractHandler):
    @web.asynchronous
    def get(self):
        self.error(message='Strona o podanym adresie nie istnieje.', code=401)
