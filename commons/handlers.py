# coding=UTF-8

from bson import ObjectId
from tornado import web
from tornado.ioloop import IOLoop

from commons import utils
from commons.constants import config, fields
from commons.context import Context
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.EmailMixin import EmailMixin
from commons.mixins.JSendMixin import JSendMixin


class AbstractHandler(web.RequestHandler, JSendMixin, DaoMixin, EmailMixin):
    SUPPORTED_METHODS = ('POST', 'OPTIONS', 'GET')

    def options(self, *args, **kwargs):
        pass

    @property
    def db(self):
        return self.application.settings[config.APPLICATION_DB]

    @property
    def config(self):
        return self.application.settings[config.APPLICATION_CONFIG]

    @property
    def aes(self):
        return self.application.settings[config.APPLICATION_AES]

    @property
    def fs(self):
        return self.application.settings[config.APPLICATION_FS]

    def get_remote_ip(self):
        return self.request.headers.get('X-Forwarded-For',
                                        self.request.headers.get('X-Real-Ip', self.request.remote_ip))

    def get_auth_http_client(self):
        return utils.http_client(self.config.PROXY_HOST, self.config.PROXY_PORT)

    async def _prepare_user(self):
        return

    async def prepare(self):

        self._context = Context(self.config, remote_ip=self.get_remote_ip(),
                                io_loop=IOLoop.current())

        try:
            self._context.user_doc = await self._prepare_user()
        except Exception as ex:
            await self.exc(ex)
            return

        if self._context.user_doc and fields.USOS_ID in self._context.user_doc:
            usos_id = self._context.user_doc[fields.USOS_ID]  # request authenticated
        else:
            usos_id = self.get_argument('usos_id', default=None)  # request authentication/register

        if usos_id:
            self._context.usos_doc = await self.db_get_usos(usos_id)

        self._context.settings = await self.db_settings(self.getUserId())
        self._context.setUp()

    def get_current_user(self):
        if hasattr(self, '_context'):
            return self._context.user_doc

    def getUsosId(self):
        if hasattr(self, '_context') and self._context.usos_doc:
            return self._context.usos_doc[fields.USOS_ID]

    def getUserId(self, return_object_id=True):
        if self.get_current_user():
            if return_object_id:
                return ObjectId(self.get_current_user()[fields.MONGO_ID])
            return self.get_current_user()[fields.MONGO_ID]

    def reset_user_cookie(self, user_id):
        self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
        encoded = self.aes.encrypt(str(user_id))
        self.set_secure_cookie(self.config.KUJON_SECURE_COOKIE, encoded, domain=self.config.SITE_DOMAIN)

    def isMobileRequest(self):
        if self.request.headers.get(config.MOBILE_X_HEADER_EMAIL, False) \
                and self.request.headers.get(config.MOBILE_X_HEADER_TOKEN, False):
            return True
        return False

    def getUserSettings(self):
        return self._context.settings

    async def usosCall(self, path, arguments=None):
        return await self._context.usosCaller.call(path, arguments)

    async def asyncCall(self, path, arguments=None, base_url=None, lang=True):
        return await self._context.asyncCaller.call_async(path, arguments, base_url, lang)


class DefaultErrorHandler(AbstractHandler):
    @web.asynchronous
    def get(self):
        self.error(message='Strona o podanym adresie nie istnieje.', code=401)
