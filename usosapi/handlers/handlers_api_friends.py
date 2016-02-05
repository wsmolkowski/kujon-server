import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.mixins.JSendMixin import JSendMixin


class FriendsSuggestionsApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        courses = {}
        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})

        for term in course_doc['course_editions']:
            for course in course_doc['course_editions'][term]:
                courses[course[constants.COURSE_ID]] = course

        suggested_participants = {}
        for course in courses:
            course_participants = yield self.db[constants.COLLECTION_PARTICIPANTS].find_one(
                {constants.COURSE_ID: course, constants.TERM_ID: courses[course][constants.TERM_ID]})
            for participant in course_participants[constants.PARTICIPANTS]:
                if not participant[constants.USER_ID] in suggested_participants:
                    suggested_participants[participant[constants.USER_ID]] = participant
                    suggested_participants[participant[constants.USER_ID]]['count'] = 1
                else:
                    suggested_participants[participant[constants.USER_ID]]['count'] += 1

        # posortowac suggested_participants

        if not suggested_participants:
            self.error("Please hold on we are looking your friends.")
        else:
            self.success(suggested_participants)
