# coding=UTF-8

import tornado.web
from handlers_api import BaseHandler

class ScheduleApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        terms = []
        terms_doc = []

        if not terms_doc:
            self.error("Poczekaj szukamy harmonoramu..")
        else:
            self.success(terms_doc)

