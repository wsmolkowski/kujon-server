import urlparse
import oauth2 as oauth
from bson import json_util

from staraapi import constants
from staraweb import settings
from staracommon import handlers


class BaseHandler(handlers.CommonHandler):
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

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

