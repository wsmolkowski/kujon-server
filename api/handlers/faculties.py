# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import config

LIMIT_FIELDS_FACULTY = (
    'logo_urls', 'stats', 'name', 'postal_address', 'fac_id', 'homepage_url', 'usos_id', 'static_map_urls',
    'phone_numbers')


class FacultyByIdApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self, faculty_id):

        try:
            faculty_doc = await self.api_faculty(faculty_id)
            if not faculty_doc:
                self.error('Nie możemy znaleźć danych dla jednostki.', code=404)
            else:
                self.success(faculty_doc, cache_age=config.SECONDS_2MONTHS)
        except Exception as ex:
            await self.exc(ex)


class FacultiesApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self):
        try:
            faculties = await self.api_faculties()
            self.success(faculties, cache_age=config.SECONDS_2MONTHS)
        except Exception as ex:
            await self.exc(ex)
