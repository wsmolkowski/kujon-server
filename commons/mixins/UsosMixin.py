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
    def usos_term(self, term_id):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.get_term_info(term_id)

        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time
        result[constants.TERM_ID] = result.pop(constants.ID)

        raise gen.Return(result)

    @gen.coroutine
    def usos_user_info(self):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.user_info()

        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time
        result[constants.TERM_ID] = result.pop(constants.ID)

        # # if user has photo - download
        # if 'has_photo' in result and result['has_photo']:
        #     result['has_photo'] = self.__build_user_info_photo(client, user_id, result[constants.ID],
        #                                                        crawl_time, usos)

        # strip english values and if value is empty change to None
        result['office_hours'] = result['office_hours']['pl']
        result['interests'] = result['interests']['pl']

        # strip empty values
        if result['homepage_url'] and result['homepage_url'] == "":
            result['homepage_url'] = None

        # strip english names from programmes description
        for programme in result['student_programmes']:
            programme['programme']['description'] = programme['programme']['description']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def usos_user_info_id(self, user_id):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.user_info_id(user_id)

        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time
        result[constants.TERM_ID] = result.pop(constants.ID)

        # # if user has photo - download
        # if 'has_photo' in result and result['has_photo']:
        #     result['has_photo'] = self.__build_user_info_photo(client, user_id, result[constants.ID],
        #                                                        crawl_time, usos)

        # strip english values and if value is empty change to None
        result['office_hours'] = result['office_hours']['pl']
        result['interests'] = result['interests']['pl']

        # strip empty values
        if result['homepage_url'] and result['homepage_url'] == "":
            result['homepage_url'] = None

        # strip english names from programmes description
        for programme in result['student_programmes']:
            programme['programme']['description'] = programme['programme']['description']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def token_verification(self, usos_doc, token):
        consumer = oauth.Consumer(usos_doc[constants.CONSUMER_KEY], usos_doc[constants.CONSUMER_SECRET])

        request_token_url = '{0}services/oauth/request_token?{1}&oauth_callback={2}'.format(
            usos_doc[constants.USOS_URL], 'scopes=studies|offline_access|student_exams|grades|crstests|email|photo|student_exams',
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
