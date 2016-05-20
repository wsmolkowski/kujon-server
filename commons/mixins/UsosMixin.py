# coding=UTF-8
import functools
import logging
from base64 import b64encode
from datetime import datetime

from tornado import gen, escape
from tornado import httpclient
from tornado.auth import OAuthMixin, _auth_return_future

from commons import constants, utils, settings
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
        usos_doc = self._find_usos()
        return usos_doc[constants.USOS_URL]

    def _find_usos(self):
        if hasattr(self, 'usos_doc'):
            return self.usos_doc

        for usos_doc in self._usoses:
            if usos_doc[constants.USOS_ID] == self.user_doc[constants.USOS_ID]:
                return usos_doc
        raise UsosClientError('Brak instancji USOS dla: {0}'.format(self.user_doc[constants.USOS_ID]))

    def _oauth_consumer_token(self):
        if not hasattr(self, 'usos_doc'):
            self.usos_doc = self._find_usos()
        return dict(key=self.usos_doc[constants.CONSUMER_KEY], secret=self.usos_doc[constants.CONSUMER_SECRET])

    @_auth_return_future
    def usos_request(self, path, user_doc, callback=None, args={}, photo=False, base_url=None):
        '''
            USOS async authenticated request

        :param path: service URI
        :param user_doc
        :param callback:
        :param args: service arguments
        :param photo: if photo to retrieve
        :param base_url: usos_url
        :return: json_decode
        '''

        if not base_url:
            url = self._oauth_base_uri() + path
        else:
            url = base_url + path

        access_token = dict(key=user_doc[constants.ACCESS_TOKEN_KEY], secret=user_doc[constants.ACCESS_TOKEN_SECRET])

        # Add the OAuth resource request signature if we have credentials
        method = "GET"
        oauth = self._oauth_request_parameters(url, access_token, args, method=method)
        args.update(oauth)

        url += "?" + urllib_parse.urlencode(args)
        http = utils.http_client()
        if photo:
            http_callback = functools.partial(self._on_usos_photo_request, callback)
        else:
            http_callback = functools.partial(self._on_usos_request, callback)

        http.fetch(url, callback=http_callback)

    def _on_usos_request(self, future, response):
        if response.error:
            msg = "Error response: {0} code: {1} fetching: {2} body: {3}".format(response.error.message,
                                                                                 response.code,
                                                                                 response.request.url,
                                                                                 response.body)

            try:
                resp = escape.json_decode(response.body)
                resp['code'] = response.code
                future.set_result(resp)
                logging.warning(msg)
                return
            except Exception, ex:
                logging.exception(ex)
                future.set_exception(UsosClientError(msg))
                return

        future.set_result(escape.json_decode(response.body))

    def _on_usos_photo_request(self, future, response):
        if response.error:
            future.set_exception(UsosClientError(
                "Error response %s fetching %s" % (response.error,
                                                   response.request.url)))
            return

        future.set_result({'photo': b64encode(response.body)})

    @gen.coroutine
    def call_async(self, path, arguments={}, base_url=None):
        '''
            USOS async non authenticated request

        :param path: service URI
        :param arguments: service arguments
        :return: json_decode
        '''
        if not base_url:
            url = self._oauth_base_uri() + path
        else:
            url = base_url + path

        url += "?" + urllib_parse.urlencode(arguments)

        http_client = utils.http_client()

        request = httpclient.HTTPRequest(url, method='GET', use_gzip=settings.COMPRESS_RESPONSE,
                                         user_agent=settings.PROJECT_TITLE)

        try:
            response = yield http_client.fetch(request)

            if response.code is not 200 and response.reason != 'OK':
                raise UsosClientError('Błedna odpowiedź USOS dla {0}'.format(url))

            result = escape.json_decode(response.body)
        except httpclient.HTTPError, ex:
            msg = "USOS HTTPError response: {0} code: {1} fetching: {2} body: {3}".format(ex.message,
                                                                                          ex.response.code,
                                                                                          ex.response.effective_url,
                                                                                          ex.response.body)
            # logging.exception(ex)
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
        result = yield self.usos_request(path=url, user_doc=self.user_doc, args=args)
        if 'code' in result:
            raise UsosClientError('Błedna odpowiedź  course_id: {0}: {1} - {2} '.format(course_id, result['code'], result['message']))

        result[constants.COURSE_NAME] = result['name']['pl']
        result.pop('name')
        result['learning_outcomes'] = result['learning_outcomes']['pl']
        result['description'] = result['description']['pl']
        result['assessment_criteria'] = result['assessment_criteria']['pl']
        result['bibliography'] = result['bibliography']['pl']
        result['practical_placement'] = result['practical_placement']['pl']
        result[constants.COURSE_ID] = course_id
        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_term(self, term_id):
        create_time = datetime.now()

        result = yield self.call_async('services/terms/term', arguments={'term_id': term_id})

        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time
        result[constants.TERM_ID] = result.pop(constants.ID)

        raise gen.Return(result)

    @gen.coroutine
    def usos_user_info(self):

        create_time = datetime.now()

        result = yield self.usos_request(path='services/users/user', user_doc=self.user_doc, args={
            'fields': 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'
        })

        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        # strip english values and if value is empty change to None
        result['office_hours'] = result['office_hours']['pl']
        result['interests'] = result['interests']['pl']

        # strip empty values
        if result['homepage_url'] and result['homepage_url'] == "":
            result['homepage_url'] = None

        # strip english names from programmes description
        for programme in result['student_programmes']:
            programme['programme']['description'] = programme['programme']['description']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def usos_user_info_id(self, user_id):

        create_time = datetime.now()

        result = yield self.usos_request(path='services/users/user', user_doc=self.user_doc, args={
            'fields': 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url',
            'user_id': user_id
        })

        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        # strip english values and if value is empty change to None
        result['office_hours'] = result['office_hours']['pl']
        result['interests'] = result['interests']['pl']

        # strip empty values
        if result['homepage_url'] and result['homepage_url'] == "":
            result['homepage_url'] = None

        # strip english names from programmes description
        for programme in result['student_programmes']:
            programme['programme']['description'] = programme['programme']['description']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def usos_faculty(self, faculty_id):
        create_time = datetime.now()

        result = yield self.call_async('services/fac/faculty', arguments={
            'fields': 'name|homepage_url|phone_numbers|postal_address|stats[course_count|programme_count|staff_count]|static_map_urls|logo_urls[100x100]',
            'fac_id': faculty_id
        })

        result[constants.FACULTY_ID] = faculty_id
        result['name'] = result['name']['pl']
        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_group(self, group_id):
        create_time = datetime.now()

        result = yield self.call_async('services/groups/group', arguments={
            'fields': 'course_unit_id|group_number|class_type_id|class_type|course_id|term_id|course_is_currently_conducted|course_assessment_criteria',
            'course_unit_id': group_id,
            'group_number': 1,
        })

        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_courses_editions(self):
        create_time = datetime.now()

        result = yield self.usos_request(path='services/courses/user', user_doc=self.user_doc, args={
            'fields': 'course_editions[course_id|course_name|term_id|course_units_ids]',
            'active_terms_only': 'false',
        })

        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

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
            result = yield self.usos_request(path='services/courses/course_edition', user_doc=self.user_doc, args=args)
        except Exception, ex:
            logging.warning("failed to fetch course_edition with %r %r due to %r", course_id, term_id, ex.message)
            raise gen.Return(None)

        result[constants.COURSE_NAME] = result[constants.COURSE_NAME]['pl']
        result[constants.COURSE_ID] = course_id
        result[constants.TERM_ID] = term_id
        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_programme(self, programme_id):
        create_time = datetime.now()

        result = yield self.call_async('services/progs/programme', arguments={
            'fields': 'id|name|mode_of_studies|level_of_studies|duration|professional_status|faculty[id|name]',
            'programme_id': programme_id,
        })

        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        result[constants.PROGRAMME_ID] = result.pop(constants.ID)

        # strip english names
        result['name'] = result['name']['pl']
        result['mode_of_studies'] = result['mode_of_studies']['pl']
        result['level_of_studies'] = result['level_of_studies']['pl']
        result['duration'] = result['duration']['pl']
        if 'faculty' in result and 'name' in result['faculty']:
            result['faculty']['name'] = result['faculty']['name']['pl']
            result['faculty'][constants.FACULTY_ID] = result['faculty']['id']
            del (result['faculty']['id'])

        raise gen.Return(result)

    @gen.coroutine
    def usos_photo(self, user_info_id):
        create_time = datetime.now()

        result = yield self.usos_request(path='services/photos/photo', user_doc=self.user_doc, args={
            'user_id': user_info_id,
        }, photo=True)

        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        result[constants.USOS_ID] = self.usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def usos_unit(self, unit_id):
        create_time = datetime.now()

        result = yield self.call_async('services/courses/unit', arguments={
            'fields': 'id|course_id|term_id|groups|classtype_id',
            'unit_id': unit_id,
        })

        result[constants.UNIT_ID] = result.pop(constants.ID)
        result[constants.USOS_ID] = self.usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        raise gen.Return(result)

    @gen.coroutine
    def time_table(self, given_date):
        create_time = datetime.now()

        result = yield self.usos_request(path='services/tt/user', user_doc=self.user_doc, args={
            'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
            'start': given_date,
            'days': '7'
        })

        tt = dict()
        tt[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        tt[constants.TT_STARTDATE] = str(given_date)
        tt[constants.CREATED_TIME] = create_time
        tt[constants.UPDATE_TIME] = create_time
        tt['tts'] = result
        tt[constants.USER_ID] = self.user_doc[constants.MONGO_ID]

        raise gen.Return(tt)

    @gen.coroutine
    def usos_subscribe(self, event_type, verify_token):
        create_time = datetime.now()
        try:
            result = yield self.usos_request(path='services/events/subscribe_event', user_doc=self.user_doc, args={
                'event_type': event_type,
                'callback_url': settings.DEPLOY_EVENT,
                'verify_token': verify_token
            })

            result['event_type'] = event_type
            result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
            result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
            result[constants.CREATED_TIME] = create_time
            result[constants.UPDATE_TIME] = create_time
        except Exception, ex:
            logging.exception(ex)

        raise gen.Return(result)

    @gen.coroutine
    def usos_unsubscribe(self, usos_doc, user_doc_archi):
        result = yield self.usos_request(path='services/events/unsubscribe', user_doc=user_doc_archi, base_url=usos_doc[constants.USOS_URL])
        logging.debug('unsubscribe ok')
        raise gen.Return(result)

    @gen.coroutine
    def subscriptions(self):
        create_time = datetime.now()

        result = yield self.usos_request(path='services/events/subscriptions', user_doc=self.user_doc)

        result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time
        result[constants.USER_ID] = self.user_doc[constants.MONGO_ID]

        raise gen.Return(result)

    @gen.coroutine
    def notifier_status(self, usos_doc):
        result = yield self.call_async(path='services/events/notifier_status', base_url=usos_doc[constants.USOS_URL])
        raise gen.Return(result)

    @gen.coroutine
    def courses_classtypes(self, usos_doc):
        result = yield self.call_async(path='services/courses/classtypes_index', base_url=usos_doc[constants.USOS_URL])
        raise gen.Return(result)
