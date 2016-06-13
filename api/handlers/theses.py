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
            users_info_doc = yield self.api_user_info()
            theses_doc = yield self.usos_theses(users_info_doc[constants.ID])

            self.success(theses_doc)
        except Exception as ex:
            yield self.exc(ex)
