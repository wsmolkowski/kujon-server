import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants

LIMIT_FIELDS = ('course_id', 'description', 'course_name')


class CourseEditionApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        parameters = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one({constants.COURSE_ID: course_id,
                                                                                  constants.TERM_ID: term_id,
                                                                                  constants.USOS_ID: parameters[constants.USOS_ID]},
                                                                                 LIMIT_FIELDS)

        if not course_doc:
            self.fail("We could not find for you course_edition with course_id: {0} term_id {1}.".format(course_id, term_id))
        else:
            self.success(course_doc)


class CoursesEditionsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.ID])},
            ('course_editions', )
        )

        if not course_doc:
            self.error("Please hold on we are looking your courses.")
        else:
            self.success(course_doc)
