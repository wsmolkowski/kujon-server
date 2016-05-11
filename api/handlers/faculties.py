# coding=UTF-8

import tornado.web

from base import BaseHandler
from commons import constants, decorators
from commons.errors import ApiError

LIMIT_FIELDS_FACULTY = (
    'logo_urls', 'stats', 'name', 'postal_address', 'fac_id', 'homepage_url', 'usos_id', 'static_map_urls',
    'phone_numbers')


class FacultyByIdApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, fac_id):

        try:
            fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one(
                {constants.FACULTY_ID: fac_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]},
                LIMIT_FIELDS_FACULTY)

            if not fac_doc:
                raise ApiError('Nie możemy znaleźć danych dla jednostki.', fac_id)

            self.success(fac_doc, cache_age=86400)
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

            # get facs from programmes
            cursor = self.db[constants.COLLECTION_PROGRAMMES].find(
                {constants.PROGRAMME_ID: {'$in': programmes_ids}}, ['programme_id', 'faculty.fac_id'])
            programmes = yield cursor.to_list(None)

            # get faculties
            faculties_ids = list()
            for programme in programmes:
                faculties_ids.append(programme['faculty']['fac_id'])

            cursor = self.db[constants.COLLECTION_FACULTIES].find(
                {constants.FACULTY_ID: {'$in': faculties_ids},
                 constants.USOS_ID: self.user_doc[constants.USOS_ID]}, LIMIT_FIELDS_FACULTY
            )

            faculties = yield cursor.to_list(None)

            self.success(faculties, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)
