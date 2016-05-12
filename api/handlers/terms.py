# coding=UTF-8

from datetime import date, datetime

import tornado.web

from base import BaseHandler
from commons import constants, decorators


class TermsApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            terms_docs = []

            courses_editions_doc = yield self.api_courses_editions()

            if courses_editions_doc:
                for term_id in courses_editions_doc['course_editions']:
                    term_doc = yield self.api_term(term_id)

                    term_doc[constants.TERM_ID] = term_id
                    today = date.today()
                    end_date = datetime.strptime(term_doc['finish_date'], "%Y-%m-%d").date()
                    if today <= end_date:
                        term_doc['active'] = True
                    else:
                        term_doc['active'] = False

                    terms_docs.append(term_doc)

            if not terms_docs:
                self.error("Poczekaj szukamy semestrów.")
            else:
                self.success(terms_docs, 2592000)
        except Exception, ex:
            yield self.exc(ex)


class TermApi(BaseHandler):
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
