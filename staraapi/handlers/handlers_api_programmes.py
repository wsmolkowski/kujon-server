import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from staraapi import constants

LIMIT_FIELDS = ('name','mode_of_studies','level_of_studies','programme_id','duration')


class ProgrammesByIdApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, programme_id):

        parameters = yield self.get_parameters()

        programme = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: programme_id}, LIMIT_FIELDS)

        if not programme:
            self.error("Please hold on we are looking your programmes.")
        else:
            self.success(programme)


class ProgrammesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: ObjectId(parameters[constants.ID])})

        programmes = []
        for program in user_info['student_programmes']:
            program_id = program['programme']['id']
            result = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: program_id}, LIMIT_FIELDS)
            programmes.append(result)

        if not programmes:
            self.error("Please hold on we are looking your programmes.")
        else:
            self.success(programmes)
