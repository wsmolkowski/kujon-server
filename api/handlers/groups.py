# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants

LIMIT_FIELDS = ('class_type_id', 'course_unit_id', constants.TERM_ID, 'lecturers')


class GroupsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course):

        parameters = yield self.get_parameters()

        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: ObjectId(parameters[
                                                                                                             constants.MONGO_ID])})

        programmes = []
        for program in user_info['student_programmes']:
            program_id = program['programme']['id']
            result = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: program_id}, LIMIT_FIELDS)
            programmes.append(result)

        if not programmes:
            self.error("Poczekaj szukamy grup.")
        else:
            self.success(programmes)
