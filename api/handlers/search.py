# coding=UTF-8

import tornado.gen
import tornado.web
from base import ApiHandler
from commons import decorators


class SearchUsersApi(ApiHandler):

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, query):
        try:

            if not self.validate_query_input(query):
                return

            add = yield self.api_search_user(query)
            self.success(add)
            return
        except Exception, ex:
            yield self.exc(ex)


class SearchCoursesApi(ApiHandler):

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, query):
        try:
            if not self.validate_query_input(query):
                return

            add = yield self.api_search_course(query)
            self.success(add)
            return
        except Exception, ex:
            yield self.exc(ex)


class SearchFacultiesApi(ApiHandler):

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, query):
        try:

            if not self.validate_query_input(query):
                return

            add = yield self.api_search_faculty(query)
            self.success(add)
            return
        except Exception, ex:
            yield self.exc(ex)