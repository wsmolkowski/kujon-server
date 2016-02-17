import json
from base64 import b64encode
import logging
import httplib2
import oauth2 as oauth
from httplib2 import socks

from staraapi import settings

URI_USER_INFO = "services/users/user?fields=id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url"
URI_USER_INFO_PHOTO = "services/photos/photo?user_id={0}"
URI_COURSES_EDITIONS_INFO = "services/courses/user?active_terms_only=false&fields=course_editions[course_id|course_name|term_id|course_units_ids]"
URI_COURSE_EDITION_INFO = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|coordinators|course_units_ids|lecturers"
URI_COURSE_EDITION_INFO_WITHOUT_PARTICIPANTS = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|coordinators|course_units_ids|lecturers"
URI_GRADES_FOR_COURSE_AND_TERM = "services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|course_units_ids"
URI_COURSES_CLASSTYPES = "services/courses/classtypes_index"
URI_PROGRAMMES = "services/progs/programme?programme_id={0}&fields=id|description|name|mode_of_studies|level_of_studies|duration"
URI_GROUPS = "services/groups/group?course_unit_id={0}&group_number=1&fields=course_unit_id|group_number|class_type_id|class_type|course_id|term_id"
URI_COURSES_UNITS = 'services/courses/unit?fields=id|course_id|term_id|groups|classtype_id&unit_id={0}'
URI_COURSE = 'services/courses/course?course_id={0}&fields=id|name|homepage_url|profile_url|is_currently_conducted|fac_id|lang_id|description|bibliography|learning_outcomes|assessment_criteria|practical_placement'
URI_FACULTY = 'services/fac/faculty?fac_id={0}&fields=name|homepage_url|phone_numbers|postal_address|logo_urls[100x100]'
URI_TT = 'services/tt/user?start={0}&days=7&fields=start_date|end_date|name'

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
        if code['status'] == '200':
            return json.loads(body)
        raise Exception("Error while fetching user info. Response code: {0} body: {1}".format(code, body))

    def user_info_photo(self, user_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_USER_INFO_PHOTO.format(user_id)))
        if code['status'] == '200':
            result = {'user_id': user_id,
                      'photo': b64encode(body)}
            return result
        else:
            logging.error("Error while fetching photo for user_id: {0}. Response code: {1} body: {2}".format(user_id, code, body))

    def programme(self, programme_id):
        if programme_id:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_PROGRAMMES.format(programme_id)))
            if code['status'] == '200':
                return json.loads(body)
            else:
                logging.error("Error while fetching programmes. Response code: {0} body: {1}".format(code, body))

    def tt(self, start_date):
        if start_date:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_TT.format(start_date)))
            if code['status'] == '200':
                return json.loads(body)
        logging.error("Error while fetching time tables for date: {0}. Response code: {1} body: {2}".format(start_date, code, body))

    def groups(self, course_unit_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_GROUPS.format(course_unit_id)))
        if code['status'] == '200':
            return json.loads(body)
        else:
            logging.error("Error while fetching groups. Response code: {0} body: {1}".format(code, body))

    def units(self, unit_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSES_UNITS.format(unit_id)))
        if code['status'] == '200':
            return json.loads(body)
        else:
            logging.error("Error while fetching units. Response code: {0} body: {1}".format(code, body))

    def courseeditions_info(self):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSES_EDITIONS_INFO))
        if code['status'] == '200':
            return json.loads(body)
        logging.error("Error while fetching courseeditions_info. Response code: {0} body: {1}".format(code, body))

    def course_edition(self, course_id, term_id, fetch_participants):
        if fetch_participants:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSE_EDITION_INFO.format(course_id, term_id)))
        else:
            code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSE_EDITION_INFO_WITHOUT_PARTICIPANTS.format(course_id, term_id)))
        if code['status'] == '200':
            return json.loads(body)
        else:
            logging.error("Error while fetching course_info {0}. Response code: {1} body: {2}".format(course_id, code, body))

    def course(self, course_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSE.format(course_id)))
        if code['status'] == '200':
            return json.loads(body)
        else:
            logging.error("Error while fetching course_id: {0}. Response code: {1} body: {2}".format(course_id, code, body))

    def grades(self, course_id, term_id):
        code, body = self.client.request(
            "{0}{1}".format(self.base_url, URI_GRADES_FOR_COURSE_AND_TERM.format(course_id, term_id)))
        if code['status'] == '200':
            return json.loads(body)
        else:
            logging.error("Error while fetching grades for term_id {0} and course_id {1}. Response code: {2} body: {3}".format(
                term_id, course_id, code, body))

    def class_types(self):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_COURSES_CLASSTYPES))
        if code['status'] == '200':
            return json.loads(body)
        else:
            logging.error("Error while fetching class_types. Response code: {0} body: {1}".format(code, body))

    def faculty(self, fac_id):
        code, body = self.client.request("{0}{1}".format(self.base_url, URI_FACULTY.format(fac_id)))
        if code['status'] == '200':
            return json.loads(body)
        else:
            logging.error("Error while fetching faculty: {0}. Response code: {1} body: {2}".format(fac_id, code, body))
