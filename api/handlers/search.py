# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators


class AbstractSearch(ApiHandler):
    @tornado.gen.coroutine
    def prepare(self):
        yield super(AbstractSearch, self).prepare()
        query = self.request.path.split('/')[-1]  # could be better?

        #  walidacja powinna być zrobiona w części klienckiej
        if len(query) <= 3 or len(query) >= 30:
            self.error('Niepoprawne zapytnie. Spróbuj wyszukać fragment dłuższy niż 3 znaki i krótszy niż 30.')

    @tornado.gen.coroutine
    def on_finish(self):
        path_split = self.request.path.split('/')
        query, endpoint = path_split[-1], path_split[-2]
        yield self.insert_search_query(query, endpoint)


class SearchUsersApi(AbstractSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_users(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.')
        except Exception as ex:
            yield self.exc(ex)


class SearchCoursesApi(AbstractSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_courses(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.')
        except Exception as ex:
            yield self.exc(ex)


class SearchFacultiesApi(AbstractSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_faculties(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.')
        except Exception as ex:
            yield self.exc(ex)


class SearchProgrammesApi(AbstractSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_programmes(query)
            if result_doc['items']:
                self.success(result_doc)
            else:
                self.error('Niestety nie znaleźliśmy danych.')
        except Exception as ex:
            yield self.exc(ex)
