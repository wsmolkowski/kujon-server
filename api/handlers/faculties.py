# coding=UTF-8

import tornado.web

from base import BaseHandler
from commons import constants, decorators
from commons.errors import ApiError
from bson.objectid import ObjectId

class FacultyByIdApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, fac_id):

        try:
            fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: fac_id,
                                        constants.USOS_ID: self.user_doc[constants.USOS_ID]})
            if fac_doc:
                fac_doc.pop('created_time')
                fac_doc.pop('update_time')
            else:
                raise ApiError("Nie możemy znaleźć danych dla jednostki", (fac_id,))
            self.success(fac_doc, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)


class FacultiesApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            users_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
                {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])})

            # get programmes for user
            programmes_ids = list()
            if 'student_programmes' in users_info_doc:
                for prog in users_info_doc['student_programmes']:
                    programmes_ids.append(prog['programme']['id'])

            #get facs from programmes
            cursor = self.db[constants.COLLECTION_PROGRAMMES].find(
                {constants.PROGRAMME_ID: {'$in': programmes_ids}}, ['programme_id', 'faculty.fac_id'])
            progs_facs = yield cursor.to_list(None)

            # get faculties
            facs_ids = list()
            for prog in progs_facs:
                facs_ids.append(prog['faculty']['fac_id'])
            cursor = self.db[constants.COLLECTION_FACULTIES].find(
                {constants.FACULTY_ID: {'$in': facs_ids}})
            faculties = yield cursor.to_list(None)
            for fac in faculties:
                fac.pop(constants.CREATED_TIME)
                fac.pop(constants.UPDATE_TIME)

            self.success(faculties, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)
