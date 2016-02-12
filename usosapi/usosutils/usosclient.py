import json
from base64 import b64encode

import httplib2
import oauth2 as oauth
from httplib2 import socks

from usosapi import settings

URI_USER_INFO = "services/users/user?fields=id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url"
URI_USER_INFO_PHOTO = "services/photos/photo?user_id={0}"
URI_COURSES_EDITIONS_INFO = "services/courses/user?active_terms_only=false&fields=course_editions"
URI_COURSE_EDITION_INFO = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|course_units_ids|lecturers|description"
URI_COURSE_EDITION_INFO_WITHOUT_PARTICIPANTS = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|course_units_ids|lecturers|description"
URI_GRADES_FOR_COURSE_AND_TERM = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|course_units_ids"
URI_COURSES_CLASSTYPES = "services/courses/classtypes_index"
URI_PROGRAMMES = "services/progs/programme?programme_id={0}&fields=id|description|name|mode_of_studies|level_of_studies|duration"
URI_GROUPS = "services/groups/group?course_unit_id={0}&group_number=1&fields=course_unit_id|group_number|class_type_id|course_id|term_id|lecturers"
URL_COURSES_UNITS = 'services/courses/unit?fields=id|course_name|course_id|term_id|groups|classtype_id|learning_outcomes|topics&unit_id={0}'


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

    @staticmethod
    def __get_proxy():
        if settings.PROXY_PORT and settings.PROXY_URL:
            return httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, settings.PROXY_URL, settings.PROXY_PORT)
        return None

    def user_info(self, user_info_id):
        if user_info_id:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_USER_INFO + '&user_id='+user_info_id))
        else:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_USER_INFO))
        if int(code['status']):
            return json.loads(body)
        raise Exception("Error while fetching user info. Response code: {0} body: {1}".format(code, body))

    def user_info_photo(self, user_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_USER_INFO_PHOTO.format(user_id)))
        if int(code['status']):
            result = {'user_id': user_id,
                      'photo': b64encode(body)}
            return result
        raise Exception("Error while fetching photo for user_id: {0}. Response code: {1} body: {2}".format(user_id, code, body))

    def programme(self, programme_id):
        if programme_id:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_PROGRAMMES.format(programme_id)))
            if int(code['status']):
                return json.loads(body)
        raise Exception("Error while fetching programmes. Response code: {0} body: {1}".format(code, body))

    def groups(self, course_unit_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_GROUPS.format(course_unit_id)))
        if int(code['status']):
            return json.loads(body)
        else:
            raise Exception("Error while fetching groups. Response code: {0} body: {1}".format(code, body))

    def units(self, unit_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URL_COURSES_UNITS.format(unit_id)))
        if int(code['status']):
            return json.loads(body)
        else:
            raise Exception("Error while fetching units. Response code: {0} body: {1}".format(code, body))

    def courseeditions_info(self):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSES_EDITIONS_INFO))
        if int(code['status']):
            return json.loads(body)
        raise Exception("Error while fetching courseeditions_info. Response code: {0} body: {1}".format(code, body))

    def course_edition(self, course_id, term_id, fetch_participants):
        if fetch_participants:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSE_EDITION_INFO.format(course_id, term_id)))
        else:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSE_EDITION_INFO_WITHOUT_PARTICIPANTS.format(course_id, term_id)))
        if int(code['status']):
            return json.loads(body)
        raise Exception(
            "Error while fetching course_info {0}. Response code: {1} body: {2}".format(course_id, code, body))

    def grades(self, course_id, term_id):
        code, body = self.client.request(
            "{0}{1}".format(self.base_url, URI_GRADES_FOR_COURSE_AND_TERM.format(course_id, term_id)))
        if int(code['status']):
            return json.loads(body)
        raise Exception(
            "Error while fetching grades for term_id {0} and course_id {1}. Response code: {2} body: {3}".format(
                term_id, course_id, code, body))

    def class_types(self):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSES_CLASSTYPES))
        if int(code['status']):
            return json.loads(body)
        raise Exception("Error while fetching class_types. Response code: {0} body: {1}".format(code, body))

