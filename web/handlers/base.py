import urlparse
import oauth2 as oauth
import tornado.gen
from commons.mixins.JSendMixin import JSendMixin
from commons import handlers, constants, settings


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
            'PROJECT_TITLE': settings.PROJECT_TITLE,
            'DEPLOY_URL': settings.DEPLOY_WEB,
            'API_URL': settings.DEPLOY_API,
            'USOS_PAIRED': usos_paired,
            'USER_SECURE_COOKIE': constants.USER_SECURE_COOKIE,
            'USER_LOGGED': True if user else False
        }

    @staticmethod
    def get_token(content):
        arr = dict(urlparse.parse_qsl(content))
        return oauth.Token(arr[constants.OAUTH_TOKEN], arr[constants.OAUTH_TOKEN_SECRET])

    _usoses = list()
    _usoses_encrypted = list()
    @tornado.gen.coroutine
    def get_usoses(self, show_encrypted):

        if not self._usoses or not self._usoses_encrypted:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find()
            while (yield cursor.fetch_next):
                usos_encrypted = cursor.next_object()
                usos_encrypted['logo'] = settings.DEPLOY_WEB + usos_encrypted['logo']
                usos = usos_encrypted.copy()
                usos = dict(self.aes.decrypt_usos(usos))

                self._usoses.append(usos)
                self._usoses_encrypted.append(usos_encrypted)
        if show_encrypted:
            raise tornado.gen.Return(self._usoses_encrypted)
        else:
            raise tornado.gen.Return(self._usoses)

    @tornado.gen.coroutine
    def get_usos(self, key, value):
        usoses = yield self.get_usoses(show_encrypted=False)

        for u in usoses:
            if u[key] == value:
                raise tornado.gen.Return(u)
        raise tornado.gen.Return(None)


