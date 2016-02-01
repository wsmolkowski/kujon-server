import json

import tornado.gen
import tornado.httpclient

import constants

URL_COURSE_INFO = '{0}/services/courses/course?course_id={1}&fields=id|name|description'
URL_TERM_INFO = '{0}/services/terms/term?term_id={1}'
URL_COURSES_UNITS = '{0}/services/courses/unit?fields=id|classtype_id&unit_id={1}'
URI_COURSES_CLASSTYPES = "{0}services/courses/classtypes_index"

@tornado.gen.coroutine
def get_courses_classtypes(usos_base_url, validate_cert=False):
    url = URI_COURSES_CLASSTYPES.format(usos_base_url)
    request = tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
        raise tornado.web.HTTPError(400, "Don't have data for course_classtypes.")

    classtypes = json.loads(response.body)
    raise tornado.gen.Return(json.dumps(classtypes))


@tornado.gen.coroutine
def get_courses_units(usos_base_url, unit_id, validate_cert=False):
    url = URL_COURSES_UNITS.format(usos_base_url, unit_id)
    request = tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
        raise tornado.web.HTTPError(400, "Don't have data for given units: {0}.".format(unit_id))

    unit = json.loads(response.body)
    unit[constants.UNIT_ID] = unit.pop('id')

    raise tornado.gen.Return(json.dumps(unit))

@tornado.gen.coroutine
def get_course_info(usos_base_url, courseId, validate_cert=False):
    url = URL_COURSE_INFO.format(usos_base_url, courseId)
    request = tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
        raise tornado.web.HTTPError(400, "Don't have data for given courseId: {0}.".format(courseId))

    course = json.loads(response.body)
    course[constants.COURSE_ID] = course.pop('id')

    raise tornado.gen.Return(json.dumps(course))


@tornado.gen.coroutine
def get_term_info(usos_base_url, term_id, validate_cert=False):
    url = URL_TERM_INFO.format(usos_base_url, term_id)
    request = tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
        raise tornado.web.HTTPError(400, "Don't have data for given term_id: {0}.".format(term_id))

    term = json.loads(response.body)
    term[constants.TERM_ID] = term.pop('id')

    raise tornado.gen.Return(json.dumps(term))
