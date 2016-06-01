# coding=UTF-8

import tornado.web

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import decorators, constants

LIMIT_FIELDS_FACULTY = (
    'logo_urls', 'stats', 'name', 'postal_address', 'fac_id', 'homepage_url', 'usos_id', 'static_map_urls',
    'phone_numbers')


class FacultyByIdApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, faculty_id):

        try:
            faculty_doc = yield self.api_faculty(faculty_id)

            if not faculty_doc:
                raise faculty_doc('Nie możemy znaleźć danych dla jednostki.', faculty_id)

            self.success(faculty_doc, cache_age=constants.SECONDS_2MONTHS)
        except Exception, ex:
            yield self.exc(ex)


class FacultiesApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            faculties = yield self.api_faculties()

            self.success(faculties, cache_age=constants.SECONDS_2MONTHS)
        except Exception, ex:
            yield self.exc(ex)
