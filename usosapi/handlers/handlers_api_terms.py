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

        terms = []
        cursor = self.db.terms.find()       #TODO: add user_id
        while (yield cursor.fetch_next):
            terms.append(cursor.next_object())
        self.write(json_util.dumps(terms))


        self.write(json_util.dumps('all terms'))


class TermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):

        parameters = self.get_parameters()

        try:
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})
        except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching user data: {0}".format(ex))

        if not term_id:
            raise tornado.web.HTTPError(400,
                                        "Don't have given courseId for user: ".format(term_id, parameters.mobile_id))

        termDoc = yield self.db.terms.find_one({constants.TERM_ID: term_id, constants.USOS_ID: user_doc[constants.USOS_ID]})

        if not termDoc:
            usos = self.get_usos(user_doc[constants.USOS_ID])
            logging.info("Course with courseId: {0} not found in mongo for user: {1}, fetching from usos.".format(
                    term_id, parameters.mobile_id))

            termDoc = yield usoshelper.get_term_info(usos[constants.URL], term_id)

            try:
                termDoc = json_util.loads(termDoc)
                termDoc[constants.USOS_ID] = user_doc[constants.USOS_ID]
                termDocId = yield motor.Op(self.db.terms.insert, termDoc)
            except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while inserting courseId to mongo {0}.".format(ex.message))

            logging.info(
                    "Course with courseId: {0} for mobile_id: {1}, fetched from usos and created with id: {2}".format(
                            term_id, parameters.mobile_id,termDocId))
        else:
            logging.info("Courses with courseId: {0} for mobile_id: {1} fetched from db with id: {2}".format(
                    term_id, parameters.mobile_id, termDoc["_id"]))

        self.write(json_util.dumps(termDoc))

