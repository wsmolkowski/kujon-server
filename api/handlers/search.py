# coding=UTF-8

from datetime import datetime

from tornado.ioloop import IOLoop

from api.handlers.base.base import BaseHandler
from commons import decorators
from commons.constants import fields, collections
from commons.usoshelper import dict_value_student_status, dict_value_staff_status

NUMBER_SEARCH_RESULTS = 20  # USOS api max


class AbstractSearch(BaseHandler):
    MIN_SEARCH = 3
    MAX_SEARCH = 30

    async def prepare(self):
        await super(AbstractSearch, self).prepare()
        query = self.request.path.split('/')[-1]  # could be better?

        #  walidacja powinna być zrobiona w części klienckiej
        if len(query) <= self.MIN_SEARCH or len(query) >= self.MAX_SEARCH:
            self.error('Wprowadź fragment dłuższy niż {0} znaki i krótszy niż {1}.'.format(self.MIN_SEARCH,
                                                                                           self.MAX_SEARCH))

    def on_finish(self):
        IOLoop.current().spawn_callback(self.db_insert, collections.SEARCH, {
            'type': self.EXCEPTION_TYPE,
            fields.USER_ID: self.get_current_user()[fields.MONGO_ID],
            fields.CREATED_TIME: datetime.now(),
            'host': self.request.host,
            'method': self.request.method,
            'path': self.request.path,
            'query': self.request.query,
            'remote_ip': self.get_remote_ip()
        }, update=False)

    async def api_search_users(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/users/search2',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[user[id|student_status|staff_status|employment_positions|titles]|match]|next_page',
                                         })

        if 'items' in search_doc:
            for elem in search_doc['items']:
                user = elem['user']

                # change student status to name
                if 'student_status' in user:
                    user['student_status'] = dict_value_student_status(user['student_status'])

                # change staff_status to dictionary
                user['staff_status'] = dict_value_staff_status(user['staff_status'])

        return search_doc

    async def api_search_courses(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/courses/search',
                                         arguments={
                                             'name': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[course_id|match]|next_page',
                                         })

        return search_doc

    async def api_search_faculties(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/fac/search',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'id|match|postal_address',
                                             'visibility': 'all'
                                         })

        return search_doc

    async def api_search_programmes(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/progs/search',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[match|programme[id|name|mode_of_studies|level_of_studies|duration|faculty[id]]]|next_page',
                                         })

        return search_doc

    async def api_search_theses(self, query):
        start = self.get_argument('start', default=0, strip=True)

        search_doc = await self.usosCall(path='services/theses/search',
                                         arguments={
                                             'query': query,
                                             'start': int(start),
                                             'num': NUMBER_SEARCH_RESULTS,
                                             'fields': 'items[match|thesis[type|id|title|authors|supervisors|faculty[id|name]]]|next_page',
                                         })

        return search_doc


class SearchUsersApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_users(query)
            self.success(result_doc)
        except Exception as ex:
            await self.exc(ex)


class SearchCoursesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_courses(query)
            self.success(result_doc)
        except Exception as ex:
            await self.exc(ex)


class SearchFacultiesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_faculties(query)
            self.success(result_doc)
        except Exception as ex:
            await self.exc(ex)


class SearchProgrammesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_programmes(query)
            self.success(result_doc)
        except Exception as ex:
            await self.exc(ex)


class SearchThesesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_theses(query)
            self.success(result_doc)
        except Exception as ex:
            await self.exc(ex)
