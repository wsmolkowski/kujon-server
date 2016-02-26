import urlparse
import oauth2 as oauth

from staraweb import settings
from staracommon.mixins.JSendMixin import JSendMixin
from staracommon import handlers, constants


class BaseHandler(handlers.CommonHandler, JSendMixin):
    @property
    def db(self):
        return self.application.db

    def template_data(self):

        user = self.get_current_user()
        if user and 'usos_paired' in user.keys():
            usos_paired = user['usos_paired']
        else:
            usos_paired = False

        return {
            'PROJECT_TITLE': settings.PROJECT_TITLE,
            'DEPLOY_URL': settings.DEPLOY_URL,
            'API_URL': settings.USOS_API,
            'USOS_PAIRED': usos_paired,
        }

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

