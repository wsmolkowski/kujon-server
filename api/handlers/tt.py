# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class TTApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, given_date):

        try:
            tt_doc = yield self.api_tt(given_date)
            if tt_doc:
                self.success(tt_doc, cache_age=constants.SECONDS_1WEEK)
            else:
                self.fail("Niepoprawny parametr wywołania. Data powinna być w formacie RRRR-MM-DD.")
        except Exception as ex:
            yield self.exc(ex)
