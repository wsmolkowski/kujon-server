# coding=UTF-8

from datetime import date, datetime

import tornado.web

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import constants, decorators


class TermsApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            terms_ordered = yield self.api_terms()

            if not terms_ordered:
                self.error("Poczekaj szukamy cykli")
            else:
                self.success(terms_ordered, 2592000)
        except Exception, ex:
            yield self.exc(ex)


class TermApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):

        try:
            term_doc = yield self.api_term(term_id)

            if not term_doc:
                self.error("Nie znaleźliśmy semestru: {0}.".format(term_id))
            else:
                self.success(term_doc, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)
