import tornado.gen
import tornado.httpclient
import json
import constants

URL_COURSE_INFO = '{0}/services/courses/course?course_id={1}&fields=id|name|description'


@tornado.gen.coroutine
def get_course_info(usos_base_url, courseId, validate_cert=False):
    url = URL_COURSE_INFO.format(usos_base_url, courseId)
    request = tornado.httpclient.HTTPRequest(url=url, method='GET', body=None, validate_cert=validate_cert)
    # TODO: przerobic zeby wsadzal do bazy nie id tylko course_id
    response = yield tornado.gen.Task(tornado.httpclient.AsyncHTTPClient().fetch, request)
    if response.code is not 200:
                raise tornado.web.HTTPError(400, "Don't have data for given courseId: {0}.".format(courseId))
    # replace course identifier received from usos from id to course_id
    courseDoc = json.loads(response.body)
    newId = courseDoc['id']
    courseDoc[constants.COURSE_ID] = newId
    del courseDoc['id']
    raise tornado.gen.Return(json.dumps(courseDoc))
