import json
import urllib

import tornado.gen
from tornado.httpclient import HTTPRequest

from commons import settings, constants, utils
from commons.errors import UsosAsyncError

URL_TERM_INFO = '{0}services/terms/term?term_id={1}'
URL_COURSES_UNITS = '{0}services/courses/unit?fields=id|course_name|course_id|term_id|groups|classtype_id|learning_outcomes|topics&unit_id={1}'
URL_COURSES_CLASSTYPES = "{0}services/courses/classtypes_index"
URL_NOTIFIER_STATUS = "{0}services/events/notifier_status"
URL_FACULTIES_SEARCH = "{0}services/fac/search?lang=pl&fields=name|homepage_url|phone_numbers|postal_address"

class UsosAsync(object):
    def __init__(self):
        self.client = self.build_client()

    @staticmethod
    def build_client():
        return utils.http_client()

    @staticmethod
    def build_request(url, validate_cert=False):
        return HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert,
                           proxy_host=settings.PROXY_URL, proxy_port=settings.PROXY_PORT)

    @staticmethod
    def validate_response(response):
        if response.code is 200 and response.reason == 'OK':
            return True
        return False

    @tornado.gen.coroutine
    def get_courses_classtypes(self, usos_base_url, validate_cert=False):
        url = URL_COURSES_CLASSTYPES.format(usos_base_url)
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)
        if self.validate_response(response):
            raise tornado.gen.Return(json.loads(response.body))
        else:
            raise UsosAsyncError(response, response, uri=request)

    @tornado.gen.coroutine
    def get_faculties(self, usos_base_url, validate_cert=False):
        url = URL_FACULTIES_SEARCH.format(usos_base_url)
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)
        if self.validate_response(response):
            raise tornado.gen.Return(json.loads(response.body))
        else:
            raise UsosAsyncError(response, response, uri=request)

    @tornado.gen.coroutine
    def get_courses_units(self, usos_base_url, unit_id, validate_cert=False):
        url = URL_COURSES_UNITS.format(usos_base_url, unit_id)
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)

        if self.validate_response(response):
            unit = json.loads(response.body)
            unit[constants.UNIT_ID] = unit.pop('id')
            raise tornado.gen.Return(unit)
        else:
            raise UsosAsyncError(response, response, uri=request, parameters=[unit_id])

    @tornado.gen.coroutine
    def get_term_info(self, usos_base_url, term_id, validate_cert=False):
        url = URL_TERM_INFO.format(usos_base_url, urllib.quote(term_id, safe=''))
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)

        if self.validate_response(response):
            term = json.loads(response.body)
            term[constants.TERM_ID] = term.pop('id')
            raise tornado.gen.Return(term)
        else:
            raise UsosAsyncError(response, response, uri=request, parameters=[term_id])

    @tornado.gen.coroutine
    def notifier_status(self, usos_base_url, validate_cert=False):
        url = URL_NOTIFIER_STATUS.format(usos_base_url)
        request = self.build_request(url=url, validate_cert=validate_cert)

        response = yield tornado.gen.Task(self.client.fetch, request)

        if self.validate_response(response):
            raise tornado.gen.Return(json.loads(response.body))
        else:
            raise UsosAsyncError(response, response, uri=request)
