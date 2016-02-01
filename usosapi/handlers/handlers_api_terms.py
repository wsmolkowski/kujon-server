import tornado.web
from bson import json_util
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants


class TermsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        terms = []
        cursor = self.db.terms.find({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})
        while (yield cursor.fetch_next):
            terms.append(cursor.next_object())
        self.write(json_util.dumps(terms))

class TermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):

        user_doc, usos_doc = yield self.get_parameters()

        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id, constants.USOS_ID: user_doc[constants.USOS_ID]})
        if not term_doc:
            pass    # TODO: return json with custom message

        self.write(json_util.dumps(term_doc))