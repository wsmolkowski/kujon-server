import tornado.web
from bson import json_util
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.mixins.JSendMixin import JSendMixin


class TermsApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        terms = []
        terms_doc = []
        courses_editions_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})

        for term in courses_editions_doc['course_editions']:
            terms.append(term)
            cursor = self.db.terms.find({constants.TERM_ID: term, constants.USOS_ID: usos_doc[constants.USOS_ID]})
            while (yield cursor.fetch_next):
                terms_doc.append(cursor.next_object())

        self.success(json_util.dumps(terms_doc))


class TermApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):

        user_doc, usos_doc = yield self.get_parameters()

        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id, constants.USOS_ID: user_doc[constants.USOS_ID]})
        if not term_doc:
            pass    # TODO: return json with custom message

        self.success(json_util.dumps(term_doc))