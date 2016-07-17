# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class CourseEditionApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        try:
            course_doc = yield self.api_course_term(course_id, term_id)
            if course_doc:
                self.success(course_doc, cache_age=constants.SECONDS_2WEEKS)
            else:
                self.error('Nie znaleziono informacji o danej edycji kursu.', code=404)
        except Exception as ex:
            yield self.exc(ex)


class CoursesApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id):

        try:
            course_doc = yield self.api_course(course_id)
            if course_doc:
                self.success(course_doc, cache_age=constants.SECONDS_2MONTHS)
            else:
                self.error('Nie znaleziono informacji o danym kursie.', code=404)
        except Exception as ex:
            yield self.exc(ex)


class CoursesEditionsApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            courses = yield self.api_courses(fields=[constants.COURSE_ID, constants.COURSE_NAME, constants.TERM_ID])
            self.success(courses, cache_age=constants.SECONDS_2WEEKS)
        except Exception as ex:
            yield self.exc(ex)


class CoursesEditionsByTermApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            courses = yield self.api_courses_by_term(
                fields=[constants.COURSE_ID, constants.COURSE_NAME, constants.TERM_ID])
            self.success(courses, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            yield self.exc(ex)
