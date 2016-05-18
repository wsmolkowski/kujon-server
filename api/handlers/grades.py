# coding=UTF-8

import tornado.gen
import tornado.web

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import decorators


class GradesForUserApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            grades_doc = yield self.api_grades()
            self.success(grades_doc, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)


class GradesForUserByTermApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            grades_doc = yield self.api_grades_byterm()
            self.success(grades_doc, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)


class GradesForCourseAndTermApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        try:
            grades_doc = yield self.api_grade(course_id, term_id)
            if not grades_doc:
                self.error("Nie ma ocen dla przedmiotu {0} i semestru {1}.".format(course_id, term_id))
            else:
                self.success(grades_doc)
        except Exception, ex:
            yield self.exc(ex)
