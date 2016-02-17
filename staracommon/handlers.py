from tornado.web import RequestHandler
from tornado import httpclient
from bson import json_util
from tornado.escape import json_decode

import settings
import utils


class CommonHandler(RequestHandler):
    USER_SECURE_COOKIE = 'USER_SECURE_COOKIE'

    def get_auth_http_client(self):
        if settings.PROXY_URL and settings.PROXY_PORT:
            httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                                 defaults=dict(proxy_host=settings.PROXY_URL,
                                                               proxy_port=settings.PROXY_PORT,
                                                               validate_cert=False))

        return httpclient.AsyncHTTPClient()

    def get_current_user(self):
        cookie = self.get_secure_cookie(self.USER_SECURE_COOKIE)
        if cookie:
            cookie = json_decode(cookie)
            return json_util.loads(cookie)
        return None

    @property
    def oauth_parameters(self):
        return {
            'proxy_info': utils.get_proxy(),
        }