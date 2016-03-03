import json
import urllib

import tornado.gen
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.web import HTTPError

from commons import settings as common_settings, constants

URL_TERM_INFO = '{0}services/terms/term?term_id={1}'
URL_COURSES_UNITS = '{0}services/courses/unit?fields=id|course_name|course_id|term_id|groups|classtype_id|learning_outcomes|topics&unit_id={1}'
URI_COURSES_CLASSTYPES = "{0}services/courses/classtypes_index"


class UsosAsync:
    def __init__(self):
        self.client = self.build_client()

    @staticmethod
    def build_client():
        if common_settings.PROXY_URL and common_settings.PROXY_PORT:
            tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                                         defaults=dict(proxy_host=common_settings.PROXY_URL,
                                                                       proxy_port=common_settings.PROXY_PORT))
        return AsyncHTTPClient()

    @staticmethod
    def build_request(url, validate_cert=False):
        return HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert,
                           proxy_host=common_settings.PROXY_URL, proxy_port=common_settings.PROXY_PORT)

    @staticmethod
    def validate_response(fetch_type, response):
        if response.code is not 200:
            raise HTTPError(response.code, "Error while fetching {0}. Response body: {1}".format(fetch_type,
                                                                                                 response.error))

    @tornado.gen.coroutine
    def get_courses_classtypes(self, usos_base_url, validate_cert=False):
        url = URI_COURSES_CLASSTYPES.format(usos_base_url)
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)
        self.validate_response('courses_classtypes', response)

        raise tornado.gen.Return(json.loads(response.body))

    @tornado.gen.coroutine
    def get_courses_units(self, usos_base_url, unit_id, validate_cert=False):
        url = URL_COURSES_UNITS.format(usos_base_url, unit_id)
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)
        self.validate_response('courses_units', response)

        unit = json.loads(response.body)
        unit[constants.UNIT_ID] = unit.pop('id')

        raise tornado.gen.Return(unit)

    @tornado.gen.coroutine
    def get_term_info(self, usos_base_url, term_id, validate_cert=False):
        url = URL_TERM_INFO.format(usos_base_url, urllib.quote(term_id, safe=''))
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)

        self.validate_response('term_info', response)

        term = json.loads(response.body)
        term[constants.TERM_ID] = term.pop('id')

        raise tornado.gen.Return(term)
