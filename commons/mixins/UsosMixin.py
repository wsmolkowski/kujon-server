# coding=UTF-8

import logging
from base64 import b64encode

from tornado import gen, escape
from tornado.auth import OAuthMixin
from tornado.httpclient import HTTPRequest

from commons import constants, settings, usoshelper
from commons.errors import UsosClientError

try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3

try:
    import urllib.parse as urllib_parse  # py3
except ImportError:
    import urllib as urllib_parse  # py2


class UsosMixin(OAuthMixin):
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False

    def _oauth_base_uri(self):
        return self.get_current_usos()[constants.USOS_URL]

    def _oauth_consumer_token(self):
        return dict(key=self.get_current_usos()[constants.CONSUMER_KEY],
                    secret=self.get_current_usos()[constants.CONSUMER_SECRET])

    @gen.coroutine
    def usos_request(self, path, arguments={}):

        arguments['lang'] = 'pl'

        url = self._oauth_base_uri() + path

        access_token = dict(key=self.get_current_user()[constants.ACCESS_TOKEN_KEY],
                            secret=self.get_current_user()[constants.ACCESS_TOKEN_SECRET])

        # Add the OAuth resource request signature if we have credentials
        oauth = self._oauth_request_parameters(url, access_token, arguments)
        arguments.update(oauth)

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        client = self.get_auth_http_client()

        response = yield client.fetch(HTTPRequest(url=url,
                                                  connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                                                  request_timeout=constants.HTTP_REQUEST_TIMEOUT))

        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            raise gen.Return(escape.json_decode(response.body))
        elif response.code == 200 and 'image/jpg' in response.headers['Content-Type']:
            raise gen.Return({'photo': b64encode(response.body)})
        else:
            raise UsosClientError('Error code: {0} with body: {1} while fetching: {2}'.format(response.code,
                                                                                              response.body,
                                                                                              url))

    @gen.coroutine
    def call_async(self, path, arguments={}, base_url=None):

        arguments['lang'] = 'pl'

        if not base_url:
            url = self._oauth_base_uri() + path
        else:
            url = base_url + path

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        client = self.get_auth_http_client()

        response = yield client.fetch(HTTPRequest(url=url,
                                                  connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                                                  request_timeout=constants.HTTP_REQUEST_TIMEOUT))

        if response.code == 200 and 'application/json' in response.headers['Content-Type']:
            raise gen.Return(escape.json_decode(response.body))
        else:
            raise UsosClientError('Error code: {0} with body: {1} while fetching: {2}'.format(response.code,
                                                                                              response.body,
                                                                                              url))

    @gen.coroutine
    def usos_course(self, course_id):

        url = 'services/courses/course'
        result = yield self.usos_request(path=url, arguments={
            'course_id': course_id,
            'fields': 'name|homepage_url|profile_url|is_currently_conducted|fac_id|lang_id|description|bibliography|learning_outcomes|assessment_criteria|practical_placement'
        })

        result[constants.COURSE_NAME] = result['name']['pl']
        result.pop('name')
        result['learning_outcomes'] = result['learning_outcomes']['pl']
        result['description'] = result['description']['pl']
        result['assessment_criteria'] = result['assessment_criteria']['pl']
        result['bibliography'] = result['bibliography']['pl']
        result['practical_placement'] = result['practical_placement']['pl']
        result[constants.COURSE_ID] = course_id

        raise gen.Return(result)

    @gen.coroutine
    def usos_term(self, term_id):
        result = yield self.call_async('services/terms/term', arguments={'term_id': term_id})

        result['name'] = result['name']['pl']
        result[constants.TERM_ID] = result.pop(constants.ID)

        raise gen.Return(result)

    @gen.coroutine
    def usos_user_info(self, user_id=None):
        fields = 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'

        if user_id:
            result = yield self.usos_request(path='services/users/user', arguments={
                'fields': fields,
                'user_id': user_id
            })
        else:
            result = yield self.usos_request(path='services/users/user', arguments={
                'fields': fields
            })

        # strip english values and if value is empty change to None
        if 'office_hours' in result and 'pl' in result['office_hours']:
            result['office_hours'] = result['office_hours']['pl']
            result['interests'] = result['interests']['pl']

        # strip empty values
        if 'homepage_url' in result and result['homepage_url'] == "":
            result['homepage_url'] = None

        if 'student_status' in result:
            result['student_status'] = usoshelper.dict_value_student_status(result['student_status'])

        # strip english names from programmes description
        if 'student_programmes' in result:
            for programme in result['student_programmes']:
                programme['programme']['description'] = programme['programme']['description']['pl']

        # change staff_status to dictionary
        result['staff_status'] = usoshelper.dict_value_staff_status(result['staff_status'])

        # strip employment_positions from english names
        for position in result['employment_positions']:
            position['position']['name'] = position['position']['name']['pl']
            position['faculty']['name'] = position['faculty']['name']['pl']

        # strip english from building name
        if 'room' in result and result['room'] and 'building_name' in result['room']:
            result['room']['building_name'] = result['room']['building_name']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def usos_faculty(self, faculty_id):
        result = yield self.call_async('services/fac/faculty', arguments={
            'fields': 'name|homepage_url|path[id|name]|phone_numbers|postal_address|stats[course_count|programme_count|staff_count]|static_map_urls|logo_urls[100x100]',
            'fac_id': faculty_id
        })

        result[constants.FACULTY_ID] = faculty_id
        result['name'] = result['name']['pl']
        if 'path' in result:
            for elem in result['path']:
                elem['name'] = elem['name']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def usos_group(self, group_id):
        result = yield self.call_async('services/groups/group', arguments={
            'fields': 'course_unit_id|group_number|class_type_id|class_type|course_id|term_id|course_is_currently_conducted|course_assessment_criteria',
            'course_unit_id': group_id,
            'group_number': 1,
        })
        raise gen.Return(result)

    @gen.coroutine
    def usos_courses_editions(self):
        result = yield self.usos_request(path='services/courses/user', arguments={
            'fields': 'course_editions[course_id|course_name|term_id|course_units_ids|grades|lecturers|participants|coordinators]',
            'active_terms_only': 'false',
        })

        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(result)

    @gen.coroutine
    def usos_course_edition(self, course_id, term_id, fetch_participants):
        if fetch_participants:
            args = {
                'fields': 'course_name|grades|participants|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            }
        else:
            args = {
                'fields': 'course_name|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            }
        result = yield self.usos_request(path='services/courses/course_edition', arguments=args)

        result[constants.COURSE_NAME] = result[constants.COURSE_NAME]['pl']
        result[constants.COURSE_ID] = course_id
        result[constants.TERM_ID] = term_id
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(result)

    @gen.coroutine
    def usos_programme(self, programme_id):

        result = yield self.call_async('services/progs/programme', arguments={
            'fields': 'name|mode_of_studies|level_of_studies|duration|professional_status|faculty[id|name]',
            'programme_id': programme_id,
        })

        result[constants.PROGRAMME_ID] = programme_id

        # strip english names
        result['name'] = result['name']['pl']
        result['mode_of_studies'] = result['mode_of_studies']['pl']
        result['level_of_studies'] = result['level_of_studies']['pl']
        result['professional_status'] = result['professional_status']['pl']
        result['duration'] = result['duration']['pl']
        if 'faculty' in result and 'name' in result['faculty']:
            result['faculty']['name'] = result['faculty']['name']['pl']
            result['faculty'][constants.FACULTY_ID] = result['faculty']['id']
            del (result['faculty']['id'])

        raise gen.Return(result)

    @gen.coroutine
    def usos_photo(self, user_info_id):
        result = yield self.usos_request(path='services/photos/photo', arguments={
            'user_id': user_info_id,
        })

        result[constants.ID] = user_info_id

        raise gen.Return(result)

    @gen.coroutine
    def usos_unit(self, unit_id):
        result = yield self.call_async('services/courses/unit', arguments={
            'fields': 'id|course_id|term_id|groups|classtype_id',
            'unit_id': unit_id,
        })

        result[constants.UNIT_ID] = result.pop(constants.ID)

        raise gen.Return(result)

    @gen.coroutine
    def time_table(self, given_date):
        result = yield self.usos_request(path='services/tt/user', arguments={
            'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
            'start': given_date,
            'days': '7'
        })

        tt = dict()
        tt[constants.TT_STARTDATE] = str(given_date)
        tt['tts'] = result
        tt[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(tt)

    @gen.coroutine
    def usos_subscribe(self, event_type, verify_token):
        callback_url = '{0}/{1}'.format(settings.DEPLOY_EVENT, self.get_current_usos()[constants.USOS_ID])
        result = yield self.usos_request(path='services/events/subscribe_event',
                                         arguments={
                                             'event_type': event_type,
                                             'callback_url': callback_url,
                                             'verify_token': verify_token
                                         })

        result['event_type'] = event_type
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]
        raise gen.Return(result)

    @gen.coroutine
    def usos_unsubscribe(self):
        result = yield self.usos_request(path='services/events/unsubscribe')
        logging.debug('unsubscribe_result: {0}'.format(result))

    @gen.coroutine
    def usos_subscriptions(self):
        result = yield self.usos_request(path='services/events/subscriptions')
        if not result:
            result = dict()
        raise gen.Return(result)

    @gen.coroutine
    def notifier_status(self, usos_doc):
        result = yield self.call_async(path='services/events/notifier_status', base_url=usos_doc[constants.USOS_URL])
        raise gen.Return(result)

    @gen.coroutine
    def courses_classtypes(self, usos_doc):
        result = yield self.call_async(path='services/courses/classtypes_index', base_url=usos_doc[constants.USOS_URL])
        raise gen.Return(result)

    @gen.coroutine
    def usos_theses(self, user_info_id):
        result = yield self.usos_request(path='services/theses/user', arguments={
            'user_id': user_info_id,
            'fields': 'authored_theses[id|type|title|authors|supervisors|faculty]',
        })

        if 'authored_theses' in result:
            for these in result['authored_theses']:
                these['faculty']['name'] = these['faculty']['name']['pl']

        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(result)
