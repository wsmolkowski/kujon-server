from bson import json_util
from tornado import httpclient
from tornado.escape import json_decode
from tornado.web import RequestHandler
import tornado.gen

import constants
import settings
import utils
from AESCipher import AESCipher


class CommonHandler(RequestHandler):
    @staticmethod
    def get_auth_http_client():
        if settings.PROXY_URL and settings.PROXY_PORT:
            httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                                 defaults=dict(proxy_host=settings.PROXY_URL,
                                                               proxy_port=settings.PROXY_PORT,
                                                               validate_cert=False))

        return httpclient.AsyncHTTPClient()

    def get_current_user(self):
        cookie = self.get_secure_cookie(constants.USER_SECURE_COOKIE)
        if cookie:
            cookie = json_decode(cookie)
            return json_util.loads(cookie)
        return None

    @property
    def oauth_parameters(self):
        return {
            'proxy_info': utils.get_proxy(),
        }

    _aes = None
    @property
    def aes(self):
        if not self._aes:
            self._aes = AESCipher()
        return self._aes

    _usoses = []

    @tornado.gen.coroutine
    def get_usoses(self):

        if not self._usoses:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find()
            while (yield cursor.fetch_next):
                usos = cursor.next_object()

                usos = self.aes.decrypt_usos(usos)

                usos['logo'] = settings.DEPLOY_WEB + usos['logo']
                self._usoses.append(usos)

        raise tornado.gen.Return(self._usoses)

    @tornado.gen.coroutine
    def get_usos(self, usos_url):
        usoses = yield self.get_usoses()

        for u in usoses:
            if u['url'] == usos_url:
                raise tornado.gen.Return(u)
        raise tornado.gen.Return(None)