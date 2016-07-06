# coding=UTF-8

import functools
import logging
from base64 import b64encode
from datetime import datetime

from tornado import gen, escape
from tornado.auth import OAuthMixin, _auth_return_future
from tornado.httpclient import HTTPRequest, HTTPError

from commons import constants, utils, settings, usoshelper
from commons.errors import UsosClientError

try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3

try:
    import urllib.parse as urllib_parse  # py3
except ImportError:
    import urllib as urllib_parse  # py2

HTTP_CONNECT_TIMEOUT = 300
HTTP_REQUEST_TIMEOUT = 300


class UsosMixin(OAuthMixin):
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False

    def _oauth_base_uri(self):
        return self.get_current_usos()[constants.USOS_URL]

    def _oauth_consumer_token(self):
        return dict(key=self.get_current_usos()[constants.CONSUMER_KEY],
                    secret=self.get_current_usos()[constants.CONSUMER_SECRET])

    @staticmethod
    def _response_ok(response):
        if response.error or response.code != 200 or response.reason != 'OK':
            return False
        return True

    @staticmethod
    def _build_exception(response):
        return UsosClientError('Response code: {0} message: {1} request url: {2} body: {3}'.format(
            response.code, response.error.message, response.request.url, response.body))

    @_auth_return_future
    def usos_request(self, path, callback=None, arguments={}, photo=False):

        arguments['lang'] = 'pl'

        url = self._oauth_base_uri() + path

        access_token = dict(key=self.get_current_user()[constants.ACCESS_TOKEN_KEY],
                            secret=self.get_current_user()[constants.ACCESS_TOKEN_SECRET])

        # Add the OAuth resource request signature if we have credentials
        method = "GET"
        oauth = self._oauth_request_parameters(url, access_token, arguments, method=method)
        arguments.update(oauth)

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)
        http_client = utils.http_client(validate_cert=self.get_current_usos()[constants.VALIDATE_SSL_CERT])
        if photo:
            http_callback = functools.partial(self._on_usos_photo_request, callback)
        else:
            http_callback = functools.partial(self._on_usos_request, callback)

        http_client.fetch(HTTPRequest(url=url, method=method, connect_timeout=HTTP_CONNECT_TIMEOUT,
                                      request_timeout=HTTP_REQUEST_TIMEOUT),
                          callback=http_callback)

    def _on_usos_request(self, future, response):
        if not self._response_ok(response):
            raise self._build_exception(response)

        future.set_result(self._build_response(response))

    def _on_usos_photo_request(self, future, response):
        if not self._response_ok(response):
            raise self._build_exception(response)

        future.set_result({'photo': b64encode(response.body)})

    def _build_response(self, response):
        result = escape.json_decode(response.body)
        if not result:
            raise self._build_exception(response)

        create_time = datetime.now()
        result[constants.USOS_ID] = self.get_current_user()[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time
        return result

    @gen.coroutine
    def call_async(self, path, arguments={}, base_url=None):

        arguments['lang'] = 'pl'

        if not base_url:
            url = self._oauth_base_uri() + path
        else:
            url = base_url + path

        if arguments:
            url += "?" + urllib_parse.urlencode(arguments)

        if constants.VALIDATE_SSL_CERT in self.get_current_usos():
            http_client = utils.http_client(validate_cert=True)
        else:
            http_client = utils.http_client()

        request = HTTPRequest(url=url, method='GET', use_gzip=True, user_agent=settings.PROJECT_TITLE
                              , connect_timeout=HTTP_CONNECT_TIMEOUT, request_timeout=HTTP_REQUEST_TIMEOUT)

        try:
            response = yield http_client.fetch(request)
            if not self._response_ok(response):
                raise self._build_exception(response)

            result = self._build_response(response)
        except HTTPError as ex:
            raise UsosClientError("USOS HTTPError response: {0} fetching: {1}".format(ex.message, url))

        raise gen.Return(result)

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
        tasks_get_faculties = list()
        for position in result['employment_positions']:
            position['position']['name'] = position['position']['name']['pl']
            position['faculty']['name'] = position['faculty']['name']['pl']
            tasks_get_faculties.append(self.api_faculty(position['faculty']['id']))
        yield tasks_get_faculties

        # strip english from building name
        if 'room' in result and result['room'] and 'building_name' in result['room']:
            result['room']['building_name'] = result['room']['building_name']['pl']

        # change course_editions_conducted to list of courses
        courses_conducted = []
        if result['course_editions_conducted']:
            tasks_courses = list()
            courses = list()
            for course_conducted in result['course_editions_conducted']:
                course_id, term_id = course_conducted['id'].split('|')
                if course_id not in courses:
                    courses.append(course_id)
                    tasks_courses.append(self.api_course(course_id))

            try:
                tasks_results = yield (tasks_courses)
                for course_doc in tasks_results:
                    courses_conducted.append({constants.COURSE_NAME: course_doc[constants.COURSE_NAME],
                                              constants.COURSE_ID: course_id,
                                              constants.TERM_ID: term_id})
            except Exception as ex:
                yield self.exc(ex, finish=False)

            result['course_editions_conducted'] = courses_conducted

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
        }, photo=True)

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
        result = yield self.usos_request(path='services/events/subscribe_event',
                                         arguments={
                                             'event_type': event_type,
                                             'callback_url': settings.DEPLOY_EVENT,
                                             'verify_token': verify_token
                                         })

        result['event_type'] = event_type
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]
        raise gen.Return(result)

    @gen.coroutine
    def usos_unsubscribe(self):
        try:
            yield self.usos_request(path='services/events/unsubscribe')
        except UsosClientError as ex:
            logging.warning(ex)
        raise gen.Return(None)

    @gen.coroutine
    def subscriptions(self):
        result = yield self.usos_request(path='services/events/subscriptions')

        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]
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
    def usos_search_users(self, query, start=0):
        result = yield self.usos_request(path='services/users/search2', arguments={
            'query': query.encode('utf-8'),
            'start': int(start),
            'num': 20,
            'fields': 'items[user[id|student_status|staff_status|employment_positions|titles]|match]|next_page',
        })

        if 'items' in result:
            for elem in result['items']:
                user = elem['user']

                # change student status to name
                if 'student_status' in user:
                    user['student_status'] = usoshelper.dict_value_student_status(user['student_status'])

                # change staff_status to dictionary
                user['staff_status'] = usoshelper.dict_value_staff_status(user['staff_status'])

                # remove english names
                for position in user['employment_positions']:
                    position['position']['name'] = position['position']['name']['pl']
                    position['faculty']['name'] = position['faculty']['name']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def usos_search_courses(self, query, start=0):
        result = yield self.call_async(path='services/courses/search', arguments={
            'name': query.encode('utf-8'),
            'start': int(start),
            'num': 20,
            'fields': 'items[course_name]|match|next_page]',
            'lang': 'pl'
        })
        raise gen.Return(result)

    @gen.coroutine
    def usos_search_faculty(self, query, start=0):
        result = yield self.call_async(path='services/fac/search', arguments={
            'query': query.encode('utf-8'),
            'start': int(start),
            'num': 20,
            'fields': 'id|match|postal_address',
            'visibility': 'all'
        })
        raise gen.Return(result)

    @gen.coroutine
    def usos_search_programmes(self, query, start=0):
        result = yield self.call_async(path='services/progs/search', arguments={
            'query': query.encode('utf-8'),
            'start': int(start),
            'num': 20,
            'fields': 'items[match|programme[id|name|mode_of_studies|level_of_studies|duration|faculty[id]]]|next_page',
            'lang': 'pl'
        })

        for programme in result['items']:
            programme['programme']['name'] = programme['programme']['name']['pl']
            programme['programme']['mode_of_studies'] = programme['programme']['mode_of_studies']['pl']
            programme['programme']['level_of_studies'] = programme['programme']['level_of_studies']['pl']
            programme['programme']['duration'] = programme['programme']['duration']['pl']

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

    @gen.coroutine
    def usos_crstests_participant(self):
        result = yield self.usos_request(path='services/crstests/participant')

        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]
        raise gen.Return(result)

    @gen.coroutine
    def usos_crstests_user_grade(self, node_id):
        result = yield self.usos_request(path='services/crstests/user_point', arguments={
            'node_id': node_id,
        })

        result = yield self.usos_request(path='services/crstests/user_grade', arguments={
            'node_id': node_id,
        })

        result[constants.NODE_ID] = node_id
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(result)
