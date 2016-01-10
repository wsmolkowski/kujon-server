import json

import oauth2 as oauth
from helpers import log_execution_time


URI_USER_INFO = "services/users/user?fields=id|first_name|last_name|student_status|sex|email|student_programmes|student_number|has_email|titles"
URI_COURSE_INFO = "services/courses/user?active_terms_only=false&fields=course_editions"
URI_GRADES_FOR_COURSE_AND_TERM = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades"

class USOSUpdater:

    def __init__(self, usosapi_base_url, consumer_key, consumer_secret, access_token_key, access_token_secret):

        self.usosapi_base_url = usosapi_base_url
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        if access_token_key:
            access_token = oauth.Token(access_token_key, access_token_secret)
        else:
            raise Exception("No access_token_key, do lepszej obslugi aby komorka sie zautoryzowala.")

        self.client = oauth.Client(consumer, access_token)

    @log_execution_time
    def request(self, url):

        resp, content = self.client.request(self.usosapi_base_url + url, 'GET')
        if resp['status'] != '200':
            msg = "Invalid USOS response: {0}" \
                  "\nRequest url: {1} " \
                  "\nResponse status: {2} " \
                  "\nResponse content: {3}".format(
                    self.usosapi_base_url, url, resp['status'], content)
            print msg
            raise Exception(msg)
        items = json.loads(content)

        return items

    def request_user_info(self):
        return self.request(URI_USER_INFO)

    def request_curse_info(self):
        return self.request(URI_COURSE_INFO)

    def request_grades_for_course(self, course_id, term_id):
        return self.request(URI_GRADES_FOR_COURSE_AND_TERM.format(course_id, term_id))

