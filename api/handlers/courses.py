# coding=UTF-8

import tornado.gen
import tornado.web

from base import BaseHandler
from commons import decorators


class CourseEditionApi(BaseHandler):

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        try:
            course_doc = yield self.api_course_term(course_id, term_id)
            self.success(course_doc, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)


class CoursesApi(BaseHandler):

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id):

        try:
            course_doc = yield self.api_course(course_id)
            self.success(course_doc, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)


class CoursesEditionsApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            courses = yield self.api_courses()
            self.success(courses, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)


class CoursesEditionsByTermApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            courses = yield self.api_courses_by_term()
            self.success(courses, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)