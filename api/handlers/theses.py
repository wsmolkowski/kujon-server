# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators


class ThesesApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            theses_doc = yield self.api_theses()
            self.success(theses_doc)
            return
        except Exception as ex:
            yield self.exc(ex)
