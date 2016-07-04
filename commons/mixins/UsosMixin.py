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

    def get_usos_id(self):
        return self.get_current_user()[constants.USOS_ID]

    def _oauth_base_uri(self):
        return self.get_current_usos()[constants.USOS_URL]

    def _oauth_consumer_token(self):
        return dict(key=self.get_current_usos()[constants.CONSUMER_KEY],
                    secret=self.get_current_usos()[constants.CONSUMER_SECRET])

    @staticmethod
    def response_ok(response):
        if response.error or response.code != 200 or response.reason != 'OK':
            return False
        return True

    @staticmethod
    def build_exception(response):
        result = escape.json_decode(response.body)
        if response.error:
            result['error'] = response.error.message
        result['code'] = response.code
        result['url'] = response.request.url
        return UsosClientError('USOS HTTP response {0}'.format(result))

    @_auth_return_future
    def usos_request(self, path, callback=None, args={}, photo=False):
        url = self._oauth_base_uri() + path

        access_token = dict(key=self.get_current_user()[constants.ACCESS_TOKEN_KEY],
                            secret=self.get_current_user()[constants.ACCESS_TOKEN_SECRET])

        # Add the OAuth resource request signature if we have credentials
        method = "GET"
        oauth = self._oauth_request_parameters(url, access_token, args, method=method)
        args.update(oauth)

        url += "?" + urllib_parse.urlencode(args)
        http_client = utils.http_client(validate_cert=self.get_current_usos()[constants.VALIDATE_SSL_CERT])
        if photo:
            http_callback = functools.partial(self._on_usos_photo_request, callback)
        else:
            http_callback = functools.partial(self._on_usos_request, callback)

        http_client.fetch(HTTPRequest(url=url, method=method, connect_timeout=HTTP_CONNECT_TIMEOUT,
                                      request_timeout=HTTP_REQUEST_TIMEOUT),
                          callback=http_callback)

    def _on_usos_request(self, future, response):
        if not self.response_ok(response):
            raise self.build_exception(response)

        future.set_result(escape.json_decode(response.body))

    def _on_usos_photo_request(self, future, response):
        if not self.response_ok(response):
            raise self.build_exception(response)

        future.set_result({'photo': b64encode(response.body)})

    @gen.coroutine
    def call_async(self, path, arguments={}, base_url=None):

        if not base_url:
            url = self._oauth_base_uri() + path
        else:
            url = base_url + path

        url += "?" + urllib_parse.urlencode(arguments)

        if constants.VALIDATE_SSL_CERT in self.get_current_usos():
            http_client = utils.http_client(validate_cert=True)
        else:
            http_client = utils.http_client()

        request = HTTPRequest(url=url, method='GET', use_gzip=True, user_agent=settings.PROJECT_TITLE
                              , connect_timeout=HTTP_CONNECT_TIMEOUT, request_timeout=HTTP_REQUEST_TIMEOUT)

        try:
            response = yield http_client.fetch(request)
            if not self.response_ok(response):
                raise self.build_exception(response)

            result = escape.json_decode(response.body)
        except HTTPError as ex:
            msg = "USOS HTTPError response: {0} fetching: {1}".format(ex.message, url)
            raise UsosClientError(msg)

        raise gen.Return(result)

    @gen.coroutine
    def usos_course(self, course_id):
        create_time = datetime.now()

        url = 'services/courses/course'
        args = {
            'course_id': course_id,
            'fields': 'name|homepage_url|profile_url|is_currently_conducted|fac_id|lang_id|description|bibliography|learning_outcomes|assessment_criteria|practical_placement'
        }
        result = yield self.usos_request(path=url, args=args)

        result[constants.COURSE_NAME] = result['name']['pl']
        result.pop('name')
        result['learning_outcomes'] = result['learning_outcomes']['pl']
        result['description'] = result['description']['pl']
        result['assessment_criteria'] = result['assessment_criteria']['pl']
        result['bibliography'] = result['bibliography']['pl']
        result['practical_placement'] = result['practical_placement']['pl']
        result[constants.COURSE_ID] = course_id
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_term(self, term_id):
        create_time = datetime.now()

        result = yield self.call_async('services/terms/term', arguments={'term_id': term_id})

        result['name'] = result['name']['pl']
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time
        result[constants.TERM_ID] = result.pop(constants.ID)

        raise gen.Return(result)

    @gen.coroutine
    def usos_user_info(self, user_id=None):

        create_time = datetime.now()

        fields = 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'

        if user_id:
            result = yield self.usos_request(path='services/users/user', args={
                'fields': fields,
                'user_id': user_id
            })
        else:
            result = yield self.usos_request(path='services/users/user', args={
                'fields': fields
            })

        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time

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
        create_time = datetime.now()

        result = yield self.call_async('services/fac/faculty', arguments={
            'fields': 'name|homepage_url|path[id|name]|phone_numbers|postal_address|stats[course_count|programme_count|staff_count]|static_map_urls|logo_urls[100x100]',
            'fac_id': faculty_id
        })

        result[constants.FACULTY_ID] = faculty_id
        result['name'] = result['name']['pl']
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_group(self, group_id):
        create_time = datetime.now()

        result = yield self.call_async('services/groups/group', arguments={
            'fields': 'course_unit_id|group_number|class_type_id|class_type|course_id|term_id|course_is_currently_conducted|course_assessment_criteria',
            'course_unit_id': group_id,
            'group_number': 1,
        })

        if result:
            result[constants.USOS_ID] = self.get_usos_id()
            result[constants.CREATED_TIME] = create_time
        else:
            raise gen.Return(None)
        raise gen.Return(result)

    @gen.coroutine
    def usos_courses_editions(self):
        create_time = datetime.now()

        result = yield self.usos_request(path='services/courses/user', args={
            'fields': 'course_editions[course_id|course_name|term_id|course_units_ids|grades|lecturers|participants|coordinators]',
            'active_terms_only': 'false',
        })

        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_course_edition(self, course_id, term_id, fetch_participants):
        create_time = datetime.now()

        try:
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
            result = yield self.usos_request(path='services/courses/course_edition', args=args)
        except Exception as ex:
            logging.warning("failed to fetch course_edition with %r %r due to %r", course_id, term_id, ex.message)
            raise gen.Return(None)

        result[constants.COURSE_NAME] = result[constants.COURSE_NAME]['pl']
        result[constants.COURSE_ID] = course_id
        result[constants.TERM_ID] = term_id
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(result)

    @gen.coroutine
    def usos_programme(self, programme_id):
        create_time = datetime.now()
        try:
            result = yield self.call_async('services/progs/programme', arguments={
                'fields': 'id|name|mode_of_studies|level_of_studies|duration|professional_status|faculty[id|name]',
                'programme_id': programme_id,
            })
        except Exception as ex:
            logging.exception(ex)
            raise gen.Return(None)

        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time

        result[constants.PROGRAMME_ID] = result.pop(constants.ID)

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
        create_time = datetime.now()

        result = yield self.usos_request(path='services/photos/photo', args={
            'user_id': user_info_id,
        }, photo=True)

        result[constants.ID] = user_info_id
        result[constants.USOS_ID] = self.usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_unit(self, unit_id):
        create_time = datetime.now()

        result = yield self.call_async('services/courses/unit', arguments={
            'fields': 'id|course_id|term_id|groups|classtype_id',
            'unit_id': unit_id,
        })

        result[constants.UNIT_ID] = result.pop(constants.ID)
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def time_table(self, given_date):
        create_time = datetime.now()

        result = yield self.usos_request(path='services/tt/user', args={
            'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
            'start': given_date,
            'days': '7'
        })

        tt = dict()
        tt[constants.USOS_ID] = self.get_usos_id()
        tt[constants.TT_STARTDATE] = str(given_date)
        tt[constants.CREATED_TIME] = create_time
        tt['tts'] = result
        tt[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(tt)

    @gen.coroutine
    def usos_subscribe(self, event_type, verify_token):
        create_time = datetime.now()
        result = yield self.usos_request(path='services/events/subscribe_event',
                                         args={
                                             'event_type': event_type,
                                             'callback_url': settings.DEPLOY_EVENT,
                                             'verify_token': verify_token
                                         })

        result['event_type'] = event_type
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time
        raise gen.Return(result)

    @gen.coroutine
    def usos_unsubscribe(self):
        result = yield self.usos_request(path='services/events/unsubscribe')

        logging.debug('unsubscribe ok')
        raise gen.Return(result)

    @gen.coroutine
    def subscriptions(self):
        create_time = datetime.now()

        result = yield self.usos_request(path='services/events/subscriptions')

        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time
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
        result = yield self.usos_request(path='services/users/search2', args={
            'query': query.encode('utf-8'),
            'start': int(start),
            'num': 20,
            'fields': 'items[user[id|student_status|staff_status|employment_positions|titles]|match]|next_page',
            'lang': 'pl'
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
            'lang': 'pl',
            'visibility': 'all'
        })
        raise gen.Return(result)

    @gen.coroutine
    def usos_search_programmes(self, query, start=0):
        result = yield self.call_async(path='services/progs/search', arguments={
            'query': query.encode('utf-8'),
            'start': int(start),
            'num': 20,
            'fields': 'id|type|title|supervisors|faculty[id|name]',
            'lang': 'pl'
        })

        raise gen.Return(result)

    @gen.coroutine
    def usos_theses(self, user_info_id):
        result = yield self.usos_request(path='services/theses/user', args={
            'user_id': user_info_id,
            'fields': 'authored_theses[id|type|title|authors|supervisors|faculty]',
        })

        if 'authored_theses' in result:
            for these in result['authored_theses']:
                these['faculty']['name'] = these['faculty']['name']['pl']

        create_time = datetime.now()
        result[constants.USOS_ID] = self.get_usos_id()
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        raise gen.Return(result)
