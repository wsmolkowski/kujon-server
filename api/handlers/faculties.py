# coding=UTF-8

import tornado.web

from base import BaseHandler
from commons import decorators

LIMIT_FIELDS_FACULTY = (
    'logo_urls', 'stats', 'name', 'postal_address', 'fac_id', 'homepage_url', 'usos_id', 'static_map_urls',
    'phone_numbers')


class FacultyByIdApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, faculty_id):

        try:
            faculty_doc = yield self.api_faculty(faculty_id)

            if not faculty_doc:
                raise faculty_doc('Nie możemy znaleźć danych dla jednostki.', faculty_id)

            self.success(faculty_doc, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)


class FacultiesApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            users_info_doc = yield self.api_user_info()

            # get programmes for user
            programmes_ids = list()
            if 'student_programmes' in users_info_doc:
                for programme in users_info_doc['student_programmes']:
                    programmes_ids.append(programme['programme']['id'])

            programmes = []
            for programme_id in programmes_ids:
                programme_doc = yield self.api_programme(programme_id)
                programmes.append(programme_doc)

            # get faculties
            faculties_ids = list()
            for programme in programmes:
                faculties_ids.append(programme['faculty']['fac_id'])

            faculties = []
            for faculty_id in faculties_ids:
                faculty_doc = yield self.api_faculty(faculty_id)
                faculties.append(faculty_doc)

            self.success(faculties, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)
