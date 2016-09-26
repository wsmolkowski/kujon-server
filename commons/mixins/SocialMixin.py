# coding=UTF-8

from tornado import escape

from commons import utils
from commons.errors import AuthenticationError


class SocialMixin(object):
    async def google_token(self, token):
        try:
            tokeninfo = await self.get_auth_http_client().fetch(
                utils.http_request(url='https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' + token,
                                   proxy_url=self._context.proxy_url, proxy_port=self._context.proxy_port))

            if tokeninfo.code == 200 and 'application/json' in tokeninfo.headers['Content-Type']:
                result = escape.json_decode(tokeninfo.body)
            else:
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))

        except Exception as ex:
            raise AuthenticationError('Błąd werifikacji tokenu Google+ {0}'.format(ex))
        else:
            return result

    async def facebook_token(self, token):
        try:
            tokeninfo = await self.get_auth_http_client().fetch(
                utils.http_request(url='https://graph.facebook.com/me?fields=id,name,email&access_token=' + token,
                                   proxy_url=self._context.proxy_url, proxy_port=self._context.proxy_port))

            if tokeninfo.code == 200 and 'application/json' in tokeninfo.headers['Content-Type']:
                result = escape.json_decode(tokeninfo.body)
            else:
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))

        except Exception as ex:
            raise AuthenticationError('Błąd werifikacji tokenu Facebook {0}'.format(ex))
        else:
            return result
