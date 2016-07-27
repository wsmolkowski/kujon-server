# coding=UTF-8

import logging

from tornado import gen, escape

from commons.errors import AuthenticationError


class SocialMixin(object):
    @gen.coroutine
    def google_token(self, token):
        try:
            tokeninfo = yield self.get_auth_http_client().fetch(
                'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' + token)
            if tokeninfo.code == 200 and 'application/json' in tokeninfo.headers['Content-Type']:
                result = escape.json_decode(tokeninfo.body)
            else:
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))

        except Exception as ex:
            logging.exception(ex)
            raise AuthenticationError('Błąd werifikacji tokenu Google+ {0}'.format(ex))
        else:
            raise gen.Return(result)

    @gen.coroutine
    def facebook_token(self, token):
        try:
            tokeninfo = yield self.get_auth_http_client().fetch(
                'https://graph.facebook.com/me?fields=id,name,email&access_token=' + token)
            if tokeninfo.code == 200 and 'application/json' in tokeninfo.headers['Content-Type']:
                result = escape.json_decode(tokeninfo.body)
            else:
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))

        except Exception as ex:
            logging.exception(ex)
            raise AuthenticationError('Błąd werifikacji tokenu Facebook {0}'.format(ex))
        else:
            raise gen.Return(result)
