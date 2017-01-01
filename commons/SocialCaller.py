# coding=UTF-8

from tornado import escape

from commons import utils
from commons.errors import AuthenticationError


class SocialCaller(object):
    def __init__(self, client=None, proxy_host=None, proxy_port=None, io_loop=None):
        if not client:
            client = utils.http_client(proxy_host, proxy_port, io_loop)
        self.client = client
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

    async def google_token(self, token):
        try:
            tokeninfo = await self.client.fetch(
                utils.http_request(url='https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' + token,
                                   proxy_host=self.proxy_host, proxy_port=self.proxy_port))

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
            tokeninfo = await self.client.fetch(
                utils.http_request(url='https://graph.facebook.com/me?fields=id,name,email&access_token=' + token,
                                   proxy_host=self.proxy_host, proxy_port=self.proxy_port))

            if tokeninfo.code == 200 and 'application/json' in tokeninfo.headers['Content-Type']:
                result = escape.json_decode(tokeninfo.body)
            else:
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))

        except Exception as ex:
            raise AuthenticationError('Błąd werifikacji tokenu Facebook {0}'.format(ex))
        else:
            return result
