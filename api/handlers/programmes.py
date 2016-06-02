# coding=UTF-8

import tornado.gen
import tornado.web

from base import ApiHandler
from commons import decorators, constants

LIMIT_FIELDS_PROGRAMMES = ('programme_id', 'description', 'name', 'mode_of_studies', 'level_of_studies', 'duration')


class ProgrammesByIdApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, programme_id):

        try:
            programme = yield self.api_programme(programme_id)

            if not programme:
                self.error("Poczekaj szukamy kierunku: {0)".format(programme_id))
            else:
                self.success(programme, cache_age=constants.SECONDS_2MONTHS)
        except Exception, ex:
            yield self.exc(ex)


class ProgrammesApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            programmes = yield self.api_programmes()
            if not programmes:
                self.error("Poczekaj szukamy kierunków.")
            else:
                self.success(programmes, cache_age=constants.SECONDS_1MONTH)
        except Exception, ex:
            yield self.exc(ex)
