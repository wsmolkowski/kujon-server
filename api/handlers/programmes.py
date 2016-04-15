# coding=UTF-8

import tornado.gen
import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants, decorators

LIMIT_FIELDS = ('name', 'mode_of_studies', 'level_of_studies', 'programme_id', 'duration')


class ProgrammesByIdApi(BaseHandler):
    @decorators.extra_headers(2592000)
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, programme_id):

        programme = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: programme_id},
                                                                            LIMIT_FIELDS)

        if not programme:
            self.error("Poczekaj szukamy kierunku: {0)".format(programme_id))
        else:
            self.success(programme)


class ProgrammesApi(BaseHandler):
    @decorators.extra_headers(2592000)
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])})

        if not user_info:
            self.error("Poczekaj szukamy danych o kursach użytkownika.")
            return

        programmes = []
        for program in user_info['student_programmes']:
            result = yield self.db[constants.COLLECTION_PROGRAMMES].find_one(
                {constants.PROGRAMME_ID: program['programme']['id']}, LIMIT_FIELDS)
            program['programme']['mode_of_studies'] = result['mode_of_studies']
            program['programme']['level_of_studies'] = result['level_of_studies']
            program['programme']['duration'] = result['duration']
            programmes.append(program)

        if not programmes:
            self.error("Poczekaj szukamy kierunków.")
        else:
            self.success(programmes)
