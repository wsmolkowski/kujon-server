# coding=UTF-8

import logging

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators


class AbstractMixinSearch(ApiHandler):
    @tornado.gen.coroutine
    def prepare(self):
        yield super(AbstractMixinSearch, self).prepare()

        logging.info('AbstractMixinSearch prepare')
        query = self.request.path.split('/')[-1]  # could be better?

        #  walidacja powinna być zrobiona w części klienckiej
        if len(query) < 3 or len(query) > 30:
            self.fail('Niepoprawne zapytnie. Spróbuj wyszukać fragment dłuższy niż 3 znaki i krótszy niż 30.')

    @tornado.gen.coroutine
    def on_finish(self):
        if not hasattr(self, '_search_options'):
            return  # exception was thrown before

        query, endpoint = self._search_options
        yield self.insert_search_query(query, endpoint)


class SearchUsersApi(AbstractMixinSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_users(query)
            self.success(result_doc)
        except Exception as ex:
            yield self.exc(ex)


class SearchCoursesApi(AbstractMixinSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_courses(query)
            self.success(result_doc)
        except Exception as ex:
            yield self.exc(ex)


class SearchFacultiesApi(AbstractMixinSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_faculties(query)
            self.success(result_doc)
        except Exception as ex:
            yield self.exc(ex)


class SearchProgrammesApi(AbstractMixinSearch):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, query):
        try:
            result_doc = yield self.api_search_programmes(query)
            self.success(result_doc)
        except Exception as ex:
            yield self.exc(ex)
