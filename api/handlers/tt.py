# coding=UTF-8

import tornado.gen
import tornado.web

from base import BaseHandler
from commons import decorators


class TTApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, given_date):

        try:
            tt_doc = yield self.api_tt(given_date)
            self.success(tt_doc, cache_age=86400)
        except Exception, ex:
            yield self.exc(ex)
