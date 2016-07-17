# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class ThesesApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            theses_doc = yield self.api_thesis()
            self.success(theses_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            yield self.exc(ex, finish=True)
