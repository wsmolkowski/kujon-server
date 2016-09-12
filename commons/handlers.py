# coding=UTF-8

from tornado import web
from tornado.util import ObjectDict

from commons import constants, utils
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

    def get_auth_http_client(self):
        return utils.http_client(self.config.PROXY_URL, self.config.PROXY_PORT)

    async def _prepare_user(self):
        return

    async def prepare(self):
        self._context = ObjectDict()
        self._context.proxy_url = self.config.PROXY_URL
        self._context.proxy_port = self.config.PROXY_PORT
        self._context.remote_ip = self.get_remote_ip()
        self._context.usoses = await self.get_usos_instances()
        self._context.user_doc = await self._prepare_user()

        if self._context.user_doc and constants.USOS_ID in self._context.user_doc:
            usos_id = self._context.user_doc[constants.USOS_ID]  # request authenticated
        else:
            usos_id = self.get_argument('usos_id', default=None)  # request authentication/register

        if usos_id:
            for usos in self._context.usoses:
                if usos[constants.USOS_ID] == usos_id:
                    self._context.usos_doc = usos

    def get_current_user(self):
        return self._context.user_doc

    def getUsosId(self):
        if hasattr(self._context,
                   'usos_doc') and self._context.usos_doc and constants.USOS_ID in self._context.usos_doc:
            return self._context.usos_doc[constants.USOS_ID]
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
