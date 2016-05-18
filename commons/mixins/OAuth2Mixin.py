# coding=UTF-8

import logging

import oauth2 as oauth
from tornado import gen

from commons import constants, settings


class OAuth2Mixin(object):
    @staticmethod
    def validate_response(content, resp):
        if 'status' not in resp or resp['status'] != '200':
            raise Exception('Invalid USOS response %s:\n%s' % (resp['status'], content))

    def oauth_client(self, consumer, usos_doc, request_token=None):
        parameters = self.oauth_parameters

        # when USOS have disabled SSL validation
        if constants.DISABLE_SSL_CERT_VALIDATION in usos_doc and constants.DISABLE_SSL_CERT_VALIDATION:
            parameters[constants.DISABLE_SSL_CERT_VALIDATION] = True

        if request_token:
            client = oauth.Client(consumer, request_token, **parameters)
        else:
            client = oauth.Client(consumer, **parameters)

        return client

    @gen.coroutine
    def token_verification(self, usos_doc, token):
        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        request_token_url = '{0}services/oauth/request_token?{1}&oauth_callback={2}'.format(
            usos_doc[constants.USOS_URL],
            'scopes=studies|offline_access|student_exams|grades|crstests|email|photo|student_exams',
            settings.CALLBACK_MOBI_URL + '?token=' + token)

        client = self.oauth_client(consumer, usos_doc)

        try:
            resp, content = client.request(request_token_url)
        except Exception, ex:
            logging.exception(ex)
            raise Exception('Wystąpił problem z połączeniem z serwerem USOS {0}'.format(ex.message))

        self.validate_response(content, resp)

        raise gen.Return(content)

    @gen.coroutine
    def usos_token_verification(self, user_doc, usos_doc, oauth_verifier):

        request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[constants.ACCESS_TOKEN_SECRET])
        request_token.set_verifier(oauth_verifier)
        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        client = self.oauth_client(consumer, usos_doc, request_token)

        access_token_url = '{0}{1}'.format(usos_doc[constants.USOS_URL], 'services/oauth/access_token')
        try:
            resp, content = client.request(access_token_url, 'GET')
        except Exception, ex:
            logging.exception(ex)
            raise Exception('Wystąpił problem z połączeniem z serwerem USOS {0}'.format(ex.message))

        self.validate_response(content, resp)

        raise gen.Return(content)

    @gen.coroutine
    def token_request(self, usos_doc):
        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        request_token_url = '{0}services/oauth/request_token?{1}&oauth_callback={2}'.format(
            usos_doc[constants.USOS_URL], 'scopes=studies|offline_access|student_exams|grades',
            settings.CALLBACK_URL)

        client = self.oauth_client(consumer, usos_doc)

        try:
            resp, content = client.request(request_token_url)
        except Exception, ex:
            logging.exception(ex)
            raise Exception('Wystąpił problem z połączeniem z serwerem USOS {0}'.format(ex.message))

        self.validate_response(content, resp)

        raise gen.Return(content)
