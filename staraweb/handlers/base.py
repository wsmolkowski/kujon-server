import urlparse

import oauth2 as oauth
from bson import json_util

from staracommon import handlers, constants
from staraweb import settings


class BaseHandler(handlers.CommonHandler):
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
            'USOS_PAIRED': usos_paired
        }

    def write_json(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json_util.dumps(data))

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

