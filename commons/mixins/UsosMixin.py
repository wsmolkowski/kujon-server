# coding=UTF-8

import json
import logging
from datetime import datetime

import oauth2 as oauth
from tornado import gen

from commons import constants, settings
from commons.errors import UsosClientError
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

        if 'has_photo' in result and result['has_photo']:
            photo_result = client.user_info_photo(self.user_doc[constants.MONGO_ID])
            if photo_result:
                result[constants.CREATED_TIME] = create_time
                result[constants.UPDATE_TIME] = create_time
                photo_doc = yield self.insert(constants.COLLECTION_PHOTOS, photo_result)
                result['has_photo'] = photo_doc
            else:
                logging.warn("no photo for user_id: %r", self.user_doc[constants.MONGO_ID])

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

        # if user has photo - download
        if 'has_photo' in result and result['has_photo']:

            photo_result = client.user_info_photo(user_id)

            if photo_result:
                result[constants.CREATED_TIME] = create_time
                result[constants.UPDATE_TIME] = create_time
                photo_doc = yield self.insert(constants.COLLECTION_PHOTOS, photo_result)
                result['has_photo'] = photo_doc
            else:
                logging.warn("no photo for user_id: %r", user_id)


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
    def usos_faculty(self, faculty_id):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.faculty(faculty_id)
        result[constants.FACULTY_ID] = faculty_id
        result['name'] = result['name']['pl']
        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_group(self, group_id, usos_doc=False):
        if not usos_doc:
            usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.groups(group_id)

        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_courses_edition(self, usos_doc=False):
        if not usos_doc:
            usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.courseeditions_info()
        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_course_edition(self, course_id, term_id, user_id=False):
        if not user_id:
            user_id = self.user_doc[constants.MONGO_ID]

        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        try:
            result = client.course_edition(course_id, term_id, fetch_participants=True)
        except UsosClientError, ex:
            logging.warn(
                'trying to fetch course_edition with {0} {1} due to {2}'.format(course_id, term_id, ex.message))
            result = client.course_edition(course_id, term_id, fetch_participants=False)

        result[constants.USER_ID] = user_id
        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_programme(self, programme_id):
        user_id = self.user_doc[constants.MONGO_ID]
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.programme(programme_id)

        result[constants.USER_ID] = user_id
        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        result[constants.PROGRAMME_ID] = result.pop(constants.ID)

        # strip english names
        result['name'] = result['name']['pl']
        result['mode_of_studies'] = result['mode_of_studies']['pl']
        result['level_of_studies'] = result['level_of_studies']['pl']
        result['duration'] = result['duration']['pl']
        if 'faculty' in result and 'name' in result['faculty']:
            result['faculty']['name'] = result['faculty']['name']['pl']
            result['faculty'][constants.FACULTY_ID] = result['faculty']['id']
            del (result['faculty']['id'])

        raise gen.Return(result)

    @gen.coroutine
    def usos_photo(self, user_info_id):
        user_id = self.user_doc[constants.MONGO_ID]
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.user_info_photo(user_info_id)

        result[constants.USER_ID] = user_id
        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

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
