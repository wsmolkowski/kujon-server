import logging

import motor
import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants
from usosapi import usoshelper


class TermsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        terms = {}
        cursor = self.db.terms.find()       #TODO: add user_id
        i=0
        while (yield cursor.fetch_next):
            obj=cursor.next_object()
            terms[i]=obj
            i=i+1
        terms = json_util.dumps(terms)
        self.write(terms)


class TermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):

        user_doc, usos_doc = yield self.get_parameters()

        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id, constants.USOS_ID: user_doc[constants.USOS_ID]})

        self.write(json_util.dumps(term_doc))