# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants, decorators

LIMIT_FIELDS = ('class_type_id', 'course_unit_id', constants.TERM_ID, 'lecturers')


class GroupsApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course):

        try:
            user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
                {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])})

            programmes = []
            for program in user_info['student_programmes']:
                program_id = program['programme']['id']
                result = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: program_id},
                                                                                 LIMIT_FIELDS)
                programmes.append(result)

            if not programmes:
                self.error("Poczekaj szukamy danych o Twoich grupach.")
            else:
                self.success(programmes, cache_age=86400)

        except Exception, ex:
            yield self.exc(ex)
