# coding=UTF-8

import tornado.gen
import tornado.web

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import decorators

LIMIT_FIELDS_PROGRAMMES = ('programme_id', 'description', 'name', 'mode_of_studies', 'level_of_studies', 'duration')


class ProgrammesByIdApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, programme_id):

        try:
            programme = yield self.api_programme(programme_id)

            if not programme:
                self.error("Poczekaj szukamy kierunku: {0)".format(programme_id))
            else:
                self.success(programme, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class ProgrammesApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            programmes = yield self.api_programmes()
            if not programmes:
                self.error("Poczekaj szukamy kierunków.")
            else:
                self.success(programmes, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)
