# coding=UTF-8

from tornado import gen
from tornado import web

from base import ApiHandler
from commons import decorators, constants

LIMIT_FIELDS_FACULTY = (
    'logo_urls', 'stats', 'name', 'postal_address', 'fac_id', 'homepage_url', 'usos_id', 'static_map_urls',
    'phone_numbers')


class FacultyByIdApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self, faculty_id):

        try:
            faculty_doc = yield self.api_faculty(faculty_id)

            if not faculty_doc:
                raise faculty_doc('Nie możemy znaleźć danych dla jednostki.', faculty_id)

            self.success(faculty_doc, cache_age=constants.SECONDS_2MONTHS)
        except Exception, ex:
            yield self.exc(ex)


class FacultiesApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            faculties = yield self.api_faculties()
            self.success(faculties, cache_age=constants.SECONDS_2MONTHS)
        except Exception, ex:
            yield self.exc(ex)
