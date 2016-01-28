import tornado.gen
import tornado.httpclient
import json

URL_COURSE_INFO = '{0}/services/courses/course?course_id={1}&fields=id|name|description'


@tornado.gen.coroutine
def get_course_info(usos_base_url, courseId, validate_cert=False):
    url = URL_COURSE_INFO.format(usos_base_url, courseId)
    request = tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
                raise tornado.web.HTTPError(400, "Don't have data for given courseId: {0}.".format(courseId))

    raise tornado.gen.Return(response.body)
