import urlparse
import httplib2
import tornado.web
import settings
import constants
import oauth2 as oauth

class Parameters:
    def __init__(self, usos_id, mobile_id, access_token_key, access_token_secret):
        self.usos_id = usos_id
        self.mobile_id = mobile_id
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie(constants.USER_SECURE_COOKIE)

    def get_parameters(self):
        return Parameters(
                self.get_argument(constants.USOS_ID, default=None, strip=True),
                self.get_argument(constants.MOBILE_ID, default=None, strip=True),
                self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True),
                self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True),
        )

    def validate_parameters(self, expected):
        if len(self.request.arguments) != expected:
            raise tornado.web.HTTPError(400, "<html><body>Arguments not supported %s</body></html>".format(
                    str(self.request.arguments)))

    def validate_usos(self, usos, parameters):
        if not usos:
            raise tornado.web.HTTPError(400,
                                        "<html><body>Usos %s not supported</body></html>".format(parameters.usos_id))

    def get_token(self, content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    def get_proxy(self):
        if settings.PROXY_PORT and settings.PROXY_URL:
            return httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP, settings.PROXY_URL, settings.PROXY_PORT)
        return None

    @staticmethod
    def template_data():
        return {
            'PROJECT_TITLE': settings.PROJECT_TITLE,
            constants.NEXT_PAGE:  "/"

        }

