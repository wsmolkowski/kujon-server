# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class GradesForUserApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            grades_doc = yield self.api_grades()
            self.success(grades_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            yield self.exc(ex)


class GradesForUserByTermApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            grades_doc = yield self.api_grades_byterm()
            self.success(grades_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            yield self.exc(ex)
