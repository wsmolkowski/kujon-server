# coding=UTF-8

import tornado.web

from base import BaseHandler
from commons import constants, decorators


class FacultyByIdApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, fac_id):

        fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: fac_id,
                                                                          constants.USOS_ID: self.user_doc[
                                                                              constants.USOS_ID]})
        if not fac_doc:
            self.fail(message="Nie możemy znaleźć jednostki: {0}.".format(fac_id))
        else:
            self.success(fac_doc, cache_age=86400)
