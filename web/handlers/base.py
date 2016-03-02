import urlparse
import oauth2 as oauth

import settings
from commons.mixins.JSendMixin import JSendMixin
from commons import handlers, constants


class BaseHandler(handlers.CommonHandler, JSendMixin):
    @property
    def db(self):
        return self.application.db

    def template_data(self):

        user = self.get_current_user()
        if user and constants.USOS_PAIRED in user.keys():
            usos_paired = user[constants.USOS_PAIRED]
        else:
            usos_paired = False

        return {
            "PROJECT_TITLE": settings.PROJECT_TITLE,
            "DEPLOY_URL": settings.DEPLOY_URL,
            "API_URL": settings.USOS_API,
            "USOS_PAIRED": usos_paired,
            "USER_SECURE_COOKIE": constants.USER_SECURE_COOKIE
        }

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

