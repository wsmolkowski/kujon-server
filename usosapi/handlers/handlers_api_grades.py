import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants


class GradesForUserApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()
        grade_docs = yield self.db[constants.COLLECTION_GRADES].find({constants.USER_ID: user_doc[constants.ID]}, {"grades": 1})
        if not grade_docs:
            pass    # TODO: return json with custom message

        self.write(json_util.dumps(grade_docs))

class GradesForCourseAndTermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        user_doc, usos_doc = yield self.get_parameters()

        grade_doc = yield self.db[constants.COLLECTION_GRADES].find_one(
                {constants.MOBILE_ID: user_doc[constants.MOBILE_ID], constants.COURSE_ID: course_id, constants.TERM_ID: term_id})
        if not grade_doc:
            pass    # TODO: return json with custom message

        self.write(json_util.dumps(grade_doc))
