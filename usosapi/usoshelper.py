import json

import tornado.gen
import tornado.httpclient

import constants

URL_COURSE_INFO = '{0}/services/courses/course?course_id={1}&fields=id|name|description'
URL_TERM_INFO = '{0}/services/terms/term?term_id={1}'


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
