import tornado.web

from handlers_api import BaseHandler
from usosapi import constants


class FacultyByIdApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, fac_id):

        parameters = yield self.get_parameters()

        fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: fac_id,
                                        constants.USOS_ID: parameters[constants.USOS_ID]})

        if not fac_doc:
            self.fail("We could not find faculty with fac_id: {0}.".format(fac_id))
        else:
            self.success(fac_doc)
