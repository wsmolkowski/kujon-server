# coding=UTF-8

from datetime import datetime

from tornado.ioloop import IOLoop

from api.handlers.base import ApiHandler
from commons import decorators, constants


class AbstractSearch(ApiHandler):
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
        IOLoop.current().spawn_callback(self.db_insert, constants.COLLECTION_SEARCH, {
            'type': self.EXCEPTION_TYPE,
            constants.USER_ID: self.get_current_user()[constants.MONGO_ID],
            constants.CREATED_TIME: datetime.now(),
            'host': self.request.host,
            'method': self.request.method,
            'path': self.request.path,
            'query': self.request.query,
            'remote_ip': self.get_remote_ip()
        })


class SearchUsersApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_users(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.', code=404)
        except Exception as ex:
            await self.exc(ex)


class SearchCoursesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_courses(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.', code=404)
        except Exception as ex:
            await self.exc(ex)


class SearchFacultiesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_faculties(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.', code=404)
        except Exception as ex:
            await self.exc(ex)


class SearchProgrammesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_programmes(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.', code=404)
        except Exception as ex:
            await self.exc(ex)


class SearchThesesApi(AbstractSearch):
    @decorators.authenticated
    async def get(self, query):
        try:
            result_doc = await self.api_search_theses(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.', code=404)
        except Exception as ex:
            await self.exc(ex)
