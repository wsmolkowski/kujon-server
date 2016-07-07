# coding=UTF-8

import json
import logging

from tornado import gen

from commons import utils
from commons.errors import AuthenticationError


class SocialMixin(object):
    @gen.coroutine
    def google_token(self, token):
        try:
            http_client = utils.http_client()
            tokeninfo = yield http_client.fetch('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' + token)
            if tokeninfo.code != 200 or tokeninfo.reason != 'OK':
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))
            result = json.loads(tokeninfo.body)
        except Exception as ex:
            logging.exception(ex)
            raise AuthenticationError('Błąd werifikacji tokenu Google+ {0}'.format(ex.message))
        else:
            raise gen.Return(result)

    @gen.coroutine
    def facebook_token(self, token):
        try:
            http_client = utils.http_client()
            tokeninfo = yield http_client.fetch(
                'https://graph.facebook.com/me?fields=id,name,email&access_token=' + token)
            if tokeninfo.code != 200 or tokeninfo.reason != 'OK':
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))
            result = json.loads(tokeninfo.body)
        except Exception as ex:
            logging.exception(ex)
            raise AuthenticationError('Błąd werifikacji tokenu Facebookn {0}'.format(ex.message))
        else:
            raise gen.Return(result)
