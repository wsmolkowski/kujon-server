import json
import urllib

import tornado.gen
import tornado.web
import tornado.httpclient

from usosapi import constants
from usosapi import settings

URL_COURSE_INFO = '{0}/services/courses/course?course_id={1}&fields=id|name|description'
URL_TERM_INFO = '{0}/services/terms/term?term_id={1}'
URL_COURSES_UNITS = '{0}/services/courses/unit?fields=id|classtype_id&unit_id={1}'
URI_COURSES_CLASSTYPES = "{0}services/courses/classtypes_index"


def build_request(url, validate_cert=False):
    return tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert,
                                          proxy_host=settings.PROXY_URL, proxy_port=settings.PROXY_PORT)


@tornado.gen.coroutine
def get_courses_classtypes(usos_base_url, validate_cert=False):
    if settings.PROXY_URL and settings.PROXY_PORT:
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                             defaults=dict(proxy_host=settings.PROXY_URL,
                                                           proxy_port=settings.PROXY_PORT))
    url = URI_COURSES_CLASSTYPES.format(usos_base_url)
    request = build_request(url=url, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
        raise tornado.web.HTTPError(response.code, "Error while fetching courses_classtypes. Response body: {0}".format(
            response.body))

    raise tornado.gen.Return(json.loads(response.body))


@tornado.gen.coroutine
def get_courses_units(usos_base_url, unit_id, validate_cert=False):
    if settings.PROXY_URL and settings.PROXY_PORT:
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                             defaults=dict(proxy_host=settings.PROXY_URL,
                                                           proxy_port=settings.PROXY_PORT))
    url = URL_COURSES_UNITS.format(usos_base_url, unit_id)
    request = build_request(url=url, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
        raise tornado.web.HTTPError(response.code,
                                    "Error while fetching courses_units for: {0}. Response body: {1}".format(
                                        unit_id, response.body))

    unit = json.loads(response.body)
    unit[constants.UNIT_ID] = unit.pop('id')

    raise tornado.gen.Return(unit)


@tornado.gen.coroutine
def get_course_info(usos_base_url, course_id, validate_cert=False):
    if settings.PROXY_URL and settings.PROXY_PORT:
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                             defaults=dict(proxy_host=settings.PROXY_URL,
                                                           proxy_port=settings.PROXY_PORT))
    url = URL_COURSE_INFO.format(usos_base_url, course_id)
    request = build_request(url=url, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
        raise tornado.web.HTTPError(response.code,
                                    "Error while fetching ourse_info for courseId: {0}. Response body: {1}".format(
                                        course_id, response.body))

    course = json.loads(response.body)
    course[constants.COURSE_ID] = course.pop('id')

    raise tornado.gen.Return(course)


@tornado.gen.coroutine
def get_term_info(usos_base_url, term_id, validate_cert=False):
    if settings.PROXY_URL and settings.PROXY_PORT:
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                             defaults=dict(proxy_host=settings.PROXY_URL,
                                                           proxy_port=settings.PROXY_PORT))


    url = URL_TERM_INFO.format(usos_base_url, urllib.quote(term_id, safe=''))
    request = build_request(url=url, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)

    if response.code is not 200:
        raise tornado.web.HTTPError(response.code,
                                    "Error while fetching term_info for term_id: {0}. Response body: {1}".format
                                    (term_id, response.body))

    term = json.loads(response.body)
    term[constants.TERM_ID] = term.pop('id')

    raise tornado.gen.Return(term)
