import json
import urllib
from base64 import b64encode

import oauth2 as oauth

from commons import utils, settings
from commons.errors import UsosClientError

URI_USER_INFO = u"services/users/user?fields=id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url"
URI_USER_INFO_PHOTO = u"services/photos/photo?user_id={0}"
URI_COURSES_EDITIONS_INFO = u"services/courses/user?active_terms_only=false&fields=course_editions[course_id|course_name|term_id|course_units_ids]"
URI_COURSE_EDITION_INFO = u"services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|coordinators|course_units_ids|lecturers"
URI_COURSE_EDITION_INFO_WITHOUT_PARTICIPANTS = u"services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|coordinators|course_units_ids|lecturers"
URI_GRADES_FOR_COURSE_AND_TERM = u"services/courses/course_edition?course_id={0}&term_id={1}&fields=course_id|course_name|term_id|grades|participants|course_units_ids"
URI_COURSES_CLASSTYPES = u"services/courses/classtypes_index"
URI_PROGRAMMES = u"services/progs/programme?programme_id={0}&fields=id|name|mode_of_studies|level_of_studies|duration|professional_status"
URI_GROUPS = u"services/groups/group?course_unit_id={0}&group_number=1&fields=course_unit_id|group_number|class_type_id|class_type|course_id|term_id|course_is_currently_conducted|course_assessment_criteria"
URI_COURSES_UNITS = u"services/courses/unit?fields=id|course_id|term_id|groups|classtype_id&unit_id={0}"
URI_COURSE = u"services/courses/course?course_id={0}&fields=id|name|homepage_url|profile_url|is_currently_conducted|fac_id|lang_id|description|bibliography|learning_outcomes|assessment_criteria|practical_placement"
URI_FACULTY = u"services/fac/faculty?fac_id={0}&fields=name|homepage_url|phone_numbers|postal_address|stats[course_count|programme_count|staff_count]|static_map_urls|logo_urls[100x100]"
URI_TT = u"services/tt/user?start={0}&days=7&fields=start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number"
URI_TERM_INFO = u"services/terms/term?term_id={0}"
URI_SUBSCRIBE_EVENT = 'services/events/subscribe_event?event_type={0}&callback_url={1}&verify_token={2}'
URI_SUBSCRIPTIONS = 'services/events/subscriptions?id|event_type|callback_url'
URI_UNSUBSCRIBE = 'services/events/unsubscribe'


class UsosClient(object):
    SUBSCRIPTION_CALLBACK = settings.DEPLOY_EVENT

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

    def _validate(self, code):
        if code.status is 200 and code.reason == 'OK':
            return True
        return False

    def _request(self, uri):
        return "{0}{1}".format(self.base_url, uri)

    def user_info(self, user_info_id):
        if user_info_id:
            request = u"{0}{1}{2}{3}".format(self.base_url, URI_USER_INFO, u"&user_id=", user_info_id)
        else:
            request = u"{0}{1}".format(self.base_url, URI_USER_INFO)

        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[user_info_id])

    def user_info_photo(self, user_id):
        request = u"{0}{1}".format(self.base_url, URI_USER_INFO_PHOTO.format(user_id))
        code, body = self.client.request(request)
        if self._validate(code):
            result = {'user_id': user_id,
                      'photo': b64encode(body)}
            return result
        else:
            raise UsosClientError(code, body, uri=request, parameters=[user_id])

    def programme(self, programme_id):
        if not programme_id:
            raise Exception(u"Cannot fetch for USOS data for empty programme parameter")

        request = u"{0}{1}".format(self.base_url, URI_PROGRAMMES.format(programme_id))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[programme_id])

    def time_table(self, start_date):
        if not start_date:
            raise Exception("Cannot fetch for USOS time table for empty start date parameter")

        request = "{0}{1}".format(self.base_url, URI_TT.format(start_date))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[start_date])

    def groups(self, course_unit_id):
        request = u"{0}{1}".format(self.base_url, URI_GROUPS.format(course_unit_id))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[course_unit_id])

    def units(self, unit_id):
        request = u"{0}{1}".format(self.base_url, URI_COURSES_UNITS.format(unit_id))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[unit_id])

    def courseeditions_info(self):
        request = u"{0}{1}".format(self.base_url, URI_COURSES_EDITIONS_INFO)
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request)

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
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[course_id, term_id, fetch_participants])

    def course(self, course_id):
        request = u"{0}{1}".format(self.base_url, URI_COURSE.format(course_id))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[course_id])

    def grades(self, course_id, term_id):
        request = "{0}{1}".format(self.base_url,
                                  URI_GRADES_FOR_COURSE_AND_TERM.format(course_id, urllib.quote(term_id, safe='')))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[course_id])

    def class_types(self):
        request = "{0}{1}".format(self.base_url, URI_COURSES_CLASSTYPES)
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request)

    def faculty(self, fac_id):
        request = "{0}{1}".format(self.base_url, URI_FACULTY.format(fac_id))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[fac_id])

    def get_term_info(self, term_id):
        request = "{0}{1}".format(self.base_url, URI_TERM_INFO.format(term_id))
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[term_id])

    def subscribe(self, event_type, verify_token):
        # crstests/user_grade, grades/grade, crstests/user_point
        request = self._request(URI_SUBSCRIBE_EVENT.format(event_type, self.SUBSCRIPTION_CALLBACK, verify_token))

        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request, parameters=[event_type, verify_token])

    def subscriptions(self):
        request = self._request(URI_SUBSCRIPTIONS)
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request)

    def unsubscribe(self):
        request = self._request(URI_UNSUBSCRIBE)
        code, body = self.client.request(request)
        if self._validate(code):
            return json.loads(body)
        else:
            raise UsosClientError(code, body, uri=request)
