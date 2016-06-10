# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import constants, decorators


class LecturersApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            lecturers_doc = yield self.api_lecturers()
            if not lecturers_doc:
                self.error("Poczekaj, szukamy informacji o Twoich nauczycielach.")
            else:
                self.success(lecturers_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            yield self.exc(ex)


class LecturerByIdApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        try:
            user_info_doc = yield self.api_lecturer(user_info_id)
            self.success(user_info_doc, cache_age=constants.SECONDS_2MONTHS)
        except Exception as ex:
            yield self.exc(ex)
