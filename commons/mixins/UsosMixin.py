# coding=UTF-8

import json
import logging
from datetime import datetime

import oauth2 as oauth
from tornado import gen

from commons import constants, settings
from commons.usosutils.usosclient import UsosClient


class UsosMixin(object):
    @gen.coroutine
    def usos_client(self):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        usos_client = UsosClient(usos_doc[constants.USOS_URL], usos_doc[constants.CONSUMER_KEY],
                                 usos_doc[constants.CONSUMER_SECRET],
                                 self.user_doc[constants.ACCESS_TOKEN_KEY],
                                 self.user_doc[constants.ACCESS_TOKEN_SECRET])

        raise gen.Return(usos_client)

    @gen.coroutine
    def usos_course(self, course):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.course(course)
        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        yield self.insert(constants.COLLECTION_COURSES, result)

        raise gen.Return(result)

    @staticmethod
    def validate_response(content, resp):
        if 'status' not in resp or resp['status'] != '200':
            raise Exception('Invalid USOS response %s:\n%s' % (resp['status'], content))

    def oauth_client(self, consumer, usos_doc):
        # when USOS have disabled SSL validation
        if constants.DISABLE_SSL_CERT_VALIDATION in usos_doc and constants.DISABLE_SSL_CERT_VALIDATION:
            params = self.oauth_parameters
            params[constants.DISABLE_SSL_CERT_VALIDATION] = True
            client = oauth.Client(consumer, **params)
        else:
            client = oauth.Client(consumer, **self.oauth_parameters)
        return client

    @gen.coroutine
    def usos_course_edition(self, course_id, term_id):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.course_edition(course_id, term_id)

        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        yield self.insert(constants.COLLECTION_COURSE_EDITION, result)

        raise gen.Return(result)

    @gen.coroutine
    def token_verification(self, usos_doc, token):
        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        request_token_url = '{0}services/oauth/request_token?{1}&oauth_callback={2}'.format(
            usos_doc[constants.USOS_URL], 'scopes=studies|offline_access|student_exams|grades',
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
    def mobile_token_verification(self, user_doc, usos_doc, oauth_verifier):

        request_token = oauth.Token(user_doc[constants.ACCESS_TOKEN_KEY], user_doc[
            constants.ACCESS_TOKEN_SECRET])
        request_token.set_verifier(oauth_verifier)
        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        client = self.oauth_client(consumer, usos_doc)

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

    @gen.coroutine
    def google_token(self, token):
        try:
            http_client = self.get_auth_http_client()
            tokeninfo = yield http_client.fetch('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' + token)
            if tokeninfo.code != 200 or tokeninfo.reason != 'OK':
                raise Exception(
                    'Token validation {0} status {1} body {2}'.format(tokeninfo.reason, tokeninfo.code, tokeninfo.body))
            result = json.loads(tokeninfo.body)
        except Exception, ex:
            logging.exception(ex)
            raise Exception('Błąd werifikacji tokenu Google+ {0}'.format(ex.message))
        else:
            raise gen.Return(result)
