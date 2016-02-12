from tornado import httpclient
from tornado.web import RequestHandler
from bson import json_util
from tornado.escape import json_decode

from usosweb import settings


class BaseHandler(RequestHandler):
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
    def db(self):
        return self.application.db

    def template_data(self):
        usos_paired = False
        user = self.get_current_user()
        if user and 'usos_paired' in user.keys():
            usos_paired = user['usos_paired']

        return {
            'PROJECT_TITLE': settings.PROJECT_TITLE,
            'DEPLOY_URL': settings.DEPLOY_URL,
            'USOS_PAIRED': usos_paired
        }

    def write_json(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json_util.dumps(data))