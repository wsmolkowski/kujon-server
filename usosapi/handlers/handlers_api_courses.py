import logging

from bson.objectid import ObjectId

import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants


class CourseHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id):

        user_doc, usos_doc = yield self.get_parameters()

        course_doc = yield self.db.courses.find_one({constants.COURSE_ID: course_id,
                                                     constants.USOS_ID: user_doc[constants.USOS_ID]})

        if not course_doc:
            pass #TODO: return json with custom message

        self.write(json_util.dumps(course_doc))


class CoursesEditionsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})

        self.write(json_util.dumps(course_doc))
