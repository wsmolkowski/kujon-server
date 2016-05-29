# coding=UTF-8

import tornado.gen
import tornado.web

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import decorators, constants


class GradesForUserApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            grades_doc = yield self.api_grades()
            self.success(grades_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception, ex:
            yield self.exc(ex)


class GradesForUserByTermApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            grades_doc = yield self.api_grades_byterm()
            self.success(grades_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception, ex:
            yield self.exc(ex)


