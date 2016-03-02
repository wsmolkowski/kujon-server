# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from commons import constants


class TermsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        terms = []
        terms_doc = []
        courses_editions_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.ID])})

        if courses_editions_doc:
            for term in courses_editions_doc['course_editions']:
                terms.append(term)
                cursor = self.db.terms.find({constants.TERM_ID: term, constants.USOS_ID: parameters[constants.USOS_ID]},
                                            ('name', 'end_date', 'finish_date', 'start_date', 'name'))
                while (yield cursor.fetch_next):
                    term_data = cursor.next_object()
                    term_data[constants.TERM_ID] = term
                    terms_doc.append(term_data)
        if not terms_doc:
            self.error("Poczekaj szukamy semestrów..")
        else:
            self.success(terms_doc)


class TermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):

        parameters = yield self.get_parameters()

        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one(
            {constants.TERM_ID: term_id, constants.USOS_ID: parameters[constants.USOS_ID]},
            ('name', 'end_date', 'finish_date', 'start_date', 'name', 'term_id'))

        if not term_doc:
            self.error("Nie znaleźliźmy semestru: {0}..".format(term_id))
        else:
            self.success(term_doc)
