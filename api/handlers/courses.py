# coding=UTF-8

import tornado.gen
import tornado.web

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import decorators, constants


class CourseEditionApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        try:
            course_doc = yield self.api_course_term(course_id, term_id)
            self.success(course_doc, cache_age=constants.SECONDS_2WEEKS)
        except Exception, ex:
            yield self.exc(ex)


class CoursesApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id):

        try:
            course_doc = yield self.api_course(course_id)
            self.success(course_doc, cache_age=constants.SECONDS_2MONTHS)
        except Exception, ex:
            yield self.exc(ex)


class CoursesEditionsApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            courses = yield self.api_courses()
            self.success(courses, cache_age=constants.SECONDS_2WEEKS)
        except Exception, ex:
            yield self.exc(ex)


class CoursesEditionsByTermApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            courses = yield self.api_courses_by_term()
            self.success(courses, cache_age=constants.SECONDS_1MONTH)
        except Exception, ex:
            yield self.exc(ex)
