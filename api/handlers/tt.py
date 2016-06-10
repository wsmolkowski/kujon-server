# coding=UTF-8

import tornado.gen
import tornado.web

from base import ApiHandler
from commons import decorators, constants


class TTApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, given_date):

        try:
            tt_doc = yield self.api_tt(given_date)
            self.success(tt_doc, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            yield self.exc(ex)
