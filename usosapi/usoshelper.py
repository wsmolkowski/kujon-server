import tornado.gen
import tornado.httpclient
import json

URL_COURSE_INFO = '{0}/services/courses/course?course_id={1}&fields=id|name|description'


@tornado.gen.coroutine
def get_course_info(usos_base_url, course_id, validate_cert=False):
    url = URL_COURSE_INFO.format(usos_base_url, course_id)
    request = tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert)

    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    raise tornado.gen.Return(json.loads(response.body))
