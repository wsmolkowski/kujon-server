# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import constants, decorators
from commons.mixins.CrsTestsMixin import CrsTestsMixin


class CrsTestsApi(ApiHandler, CrsTestsMixin):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            crstests_doc = yield self.api_crstests()
            if not crstests_doc:
                self.error("Brak inforamcji o Twoich sprawdzianach.", code=404)
            else:
                self.success(crstests_doc, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            yield self.exc(ex)


class CrsTestsNodeApi(ApiHandler, CrsTestsMixin):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, node_id):

        try:
            crstest_node_doc = yield self.api_crstests_grades(node_id)

            if not crstest_node_doc:
                self.error("Brak informacji o danym sprawdzianie.", code=404)
            else:
                self.success(crstest_node_doc, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            yield self.exc(ex)
