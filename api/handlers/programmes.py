# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants

LIMIT_FIELDS = ('name', 'mode_of_studies', 'level_of_studies', 'programme_id', 'duration')


class ProgrammesByIdApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, programme_id):

        parameters = yield self.get_parameters()

        programme = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: programme_id},
                                                                            LIMIT_FIELDS)

        if not programme:
            self.error(u"Poczekaj szukamy kierunku: {0)".format(programme_id))
        else:
            self.success(programme)


class ProgrammesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.ID])})

        if not user_info:
            self.error(u"Poczekaj szukamy danych o kursach użytkownika..")

        programmes = []
        for program in user_info['student_programmes']:
            result = yield self.db[constants.COLLECTION_PROGRAMMES].find_one(
                {constants.PROGRAMME_ID: program['programme']['id']}, LIMIT_FIELDS)
            program['programme']['mode_of_studies'] = result['mode_of_studies']
            program['programme']['level_of_studies'] = result['level_of_studies']
            program['programme']['duration'] = result['duration']
            programmes.append(program)

        if not programmes:
            self.error(u"Poczekaj szukamy kierunków...")
        else:
            self.success(programmes)
