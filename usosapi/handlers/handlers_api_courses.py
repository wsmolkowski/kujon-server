import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.mixins.JSendMixin import JSendMixin


class CourseHandlerApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id):

        parameters = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one({constants.COURSE_ID: course_id,
                                                     constants.USOS_ID: parameters[constants.USOS_ID]},
                                                                          ('course_id', 'description', 'name'))

        if not course_doc:
            self.fail("We could not find for you course with id: {0}".format(course_id))
        else:
            self.success(course_doc)


class CoursesEditionsApi(BaseHandler, JSendMixin):
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
