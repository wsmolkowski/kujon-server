import json
import urllib
from base64 import b64encode

import oauth2 as oauth

from commons import utils

URI_USER_INFO = u"services/users/user?fields=id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url"
URI_USER_INFO_PHOTO = u"services/photos/photo?user_id={0}"
URI_COURSES_EDITIONS_INFO = u"services/courses/user?active_terms_only=false&fields=course_editions[course_id|course_name|term_id|course_units_ids]"
URI_COURSE_EDITION_INFO = u"services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|coordinators|course_units_ids|lecturers"
URI_COURSE_EDITION_INFO_WITHOUT_PARTICIPANTS = u"services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|coordinators|course_units_ids|lecturers"
URI_GRADES_FOR_COURSE_AND_TERM = u"services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|course_units_ids"
URI_COURSES_CLASSTYPES = u"services/courses/classtypes_index"
URI_PROGRAMMES = u"services/progs/programme?programme_id={0}&fields=id|description|name|mode_of_studies|level_of_studies|duration"
URI_GROUPS = u"services/groups/group?course_unit_id={0}&group_number=1&fields=course_unit_id|group_number|class_type_id|class_type|course_id|term_id|course_is_currently_conducted|course_assessment_criteria"
URI_COURSES_UNITS = u"services/courses/unit?fields=id|course_id|term_id|groups|classtype_id&unit_id={0}"
URI_COURSE = u"services/courses/course?course_id={0}&fields=id|name|homepage_url|profile_url|is_currently_conducted|fac_id|lang_id|description|bibliography|learning_outcomes|assessment_criteria|practical_placement"
URI_FACULTY = u"services/fac/faculty?fac_id={0}&fields=name|homepage_url|phone_numbers|postal_address|logo_urls[100x100]"
URI_TT = u"services/tt/user?start={0}&days=7&fields=start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number"


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
            'proxy_info': utils.get_proxy()
        }

        self.client = oauth.Client(consumer=self.consumer, token=self.token, **self.parameters)

    def user_info(self, user_info_id):
        if user_info_id:
            code, body = self.client.request(
                u"{0}{1}{2}{3}".format(self.base_url, URI_USER_INFO, u"&user_id=", user_info_id))
        else:
            code, body = self.client.request(u"{0}{1}".format(self.base_url, URI_USER_INFO))
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(u"Error while fetching user info. Response code: {0} body: {1}".format(code, body))

    def user_info_photo(self, user_id):
        request = u"{0}{1}".format(self.base_url, URI_USER_INFO_PHOTO.format(user_id))
        code, body = self.client.request(request)
        if code['status'] == '200':
            result = {'user_id': user_id,
                      'photo': b64encode(body)}
            return result
        raise Exception(
            u"Error while fetching photo for request: {0}. Response code: {1} body: {2}".format(request, code, body))

    def programme(self, programme_id):
        if not programme_id:
            raise Exception(u"Cannot fetch for USOS data for empty programme parameter")

        request = u"{0}{1}".format(self.base_url, URI_PROGRAMMES.format(programme_id))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching programmes for requesst: {0}. Response code: {1} body: {2}".format(request, code,
                                                                                                      body))

    def tt(self, start_date):
        if not start_date:
            raise Exception(u"Cannot fetch for USOS time table for empty start date parameter")

        request = u"{0}{1}".format(self.base_url, URI_TT.format(start_date))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(u"Error while fetching time tables for request: {0}. Response code: {1} body: {2}".
                        format(request, code, body))

    def groups(self, course_unit_id):
        request = u"{0}{1}".format(self.base_url, URI_GROUPS.format(course_unit_id))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching groups for request: {0}. Response code: {1} body: {2}".format(request, code, body))

    def units(self, unit_id):
        request = u"{0}{1}".format(self.base_url, URI_COURSES_UNITS.format(unit_id))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching units for request {0}. Response code: {1} body: {2}".format(request, code, body))

    def courseeditions_info(self):
        request = u"{0}{1}".format(self.base_url, URI_COURSES_EDITIONS_INFO)
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching courseeditions_info for request: {0}. Response code: {1} body: {2}".format(request,
                                                                                                              code,
                                                                                                              body))

    def course_edition(self, course_id, term_id, fetch_participants):
        if fetch_participants:
            request = u"{0}{1}".format(self.base_url,
                                       URI_COURSE_EDITION_INFO.format(course_id, urllib.quote(term_id, safe='')))
        else:
            request = u"{0}{1}".format(self.base_url, URI_COURSE_EDITION_INFO_WITHOUT_PARTICIPANTS.format(course_id,
                                                                                                          urllib.quote(
                                                                                                              term_id,
                                                                                                              safe='')))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching course_info for request: {0}. Response code: {1} body: {2}".format(request,
                                                                                                      course_id, code,
                                                                                                      body))

    def course(self, course_id):
        request = u"{0}{1}".format(self.base_url, URI_COURSE.format(course_id))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching course_id for request: {0}. Response code: {1} body: {2}".format(request, code,
                                                                                                    body))

    def grades(self, course_id, term_id):
        request = "{0}{1}".format(self.base_url,
                                  URI_GRADES_FOR_COURSE_AND_TERM.format(course_id, urllib.quote(term_id, safe='')))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching grades for request: {0}. Response code: {1} body: {2}".format(request, code, body))

    def class_types(self):
        request = "{0}{1}".format(self.base_url, URI_COURSES_CLASSTYPES)
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(
            u"Error while fetching class_types for request {0}. Response code: {1} body: {2}".format(request, code,
                                                                                                     body))

    def faculty(self, fac_id):
        request = "{0}{1}".format(self.base_url, URI_FACULTY.format(fac_id))
        code, body = self.client.request(request)
        if code['status'] == '200':
            return json.loads(body)
        raise Exception(u"Error while fetching faculty: {0}. Response code: {1} body: {2}".format(fac_id, code, body))
