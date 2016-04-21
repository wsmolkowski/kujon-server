# coding=UTF-8

import tornado.gen
import tornado.web

from base import BaseHandler
from commons import decorators


class LecturersApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            lecturers_doc = yield self.api_lecturers()
            if not lecturers_doc:
                self.error("Poczekaj, szukamy informacji o Twoich nauczycielach.")
            else:
                self.success(lecturers_doc, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class LecturerByIdApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        try:
            user_info = yield self.api_lecturer(user_info_id)
            self.success(user_info, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)
