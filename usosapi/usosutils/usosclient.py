import httplib2
import oauth2 as oauth
from httplib2 import socks

from usosapi import settings

URI_USER_INFO = "services/users/user?fields=id|first_name|last_name|student_status|sex|email|student_programmes|student_number|has_email|titles|has_photo|photo_urls|course_editions_conducted"
URI_COURSESEDITIONS_INFO = "services/courses/user?active_terms_only=false&fields=course_editions"
URI_COURSE_INFO = "services/courses/course?course_id={0}&fields=id|name|description"
URI_GRADES_FOR_COURSE_AND_TERM = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|course_units_ids"
URI_COURSES_CLASSTYPES = "services/courses/classtypes_index"


class UsosClient:
    def __init__(self, base_url, consumer_key, consumer_secret, access_token_key, access_token_secret):
        self.base_url = base_url
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        self.token = oauth.Token(key=self.access_token_key, secret=self.access_token_secret)
        self.consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)

        self.parameters = {
            'proxy_info': self.__get_proxy()
        }

        self.client = oauth.Client(consumer=self.consumer, token=self.token, **self.parameters)

    def __get_proxy(self):
        if settings.PROXY_PORT and settings.PROXY_URL:
            return httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, settings.PROXY_URL, settings.PROXY_PORT)
        return None

    def user_info(self):
        return self.client.request("{0}{1}".format(self.base_url, URI_USER_INFO))

    def courseeditions_info(self):
        return self.client.request("{0}{1}".format(self.base_url, URI_COURSESEDITIONS_INFO))

    def course_info(self, course_id):
        return self.client.request("{0}{1}".format(self.base_url, URI_COURSE_INFO.format(course_id)))

    def grades(self, course_id, term_id):
        return self.client.request(
            "{0}{1}".format(self.base_url, URI_GRADES_FOR_COURSE_AND_TERM.format(course_id, term_id)))

    def class_types(self):
        return self.client.request("{0}{1}".format(self.base_url, URI_COURSES_CLASSTYPES))