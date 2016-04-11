# coding=UTF-8

from datetime import date, datetime

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants, decorators

TERM_LIMIT_FIELDS = ('name', 'end_date', 'finish_date', 'start_date', 'name', 'term_id')


class TermsApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        terms = []
        terms_doc = []
        courses_editions_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])})

        if courses_editions_doc:
            for term in courses_editions_doc['course_editions']:
                terms.append(term)
                cursor = self.db[constants.COLLECTION_TERMS].find(
                    {constants.TERM_ID: term, constants.USOS_ID: self.user_doc[constants.USOS_ID]},
                    ('name', 'end_date', 'finish_date', 'start_date', 'name'))
                while (yield cursor.fetch_next):
                    term_data = cursor.next_object()
                    term_data[constants.TERM_ID] = term
                    today = date.today()
                    end_date = datetime.strptime(term_data['finish_date'], "%Y-%m-%d").date()
                    if today <= end_date:
                        term_data['active'] = True
                    else:
                        term_data['active'] = False
                    terms_doc.append(term_data)
        if not terms_doc:
            self.error("Poczekaj szukamy semestrów.")
        else:
            self.success(terms_doc)


class TermApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):

        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one(
            {constants.TERM_ID: term_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}, TERM_LIMIT_FIELDS)

        if not term_doc:
            self.error("Nie znaleźliśmy semestru: {0}.".format(term_id))
        else:
            self.success(term_doc)
