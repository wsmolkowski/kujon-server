import tornado.web
from bson import json_util
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants


class GradesForUserApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()
        grades = []
        cursor = self.db[constants.COLLECTION_GRADES].find({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})
        while (yield cursor.fetch_next):
            g = cursor.next_object()
            units = []
            for unit in g['grades']['course_units_grades']:
                pipeline = [{'$match': {'unit_id': int(unit)}},{'$lookup': {'from': 'courses_classtypes', 'localField': 'classtype_id', 'foreignField': 'id', 'as': 'courses_classtypes'}}]
                unit_coursor = self.db[constants.COLLECTION_COURSES_UNITS].aggregate(pipeline)
                u = yield unit_coursor.to_list(None)
                units.append(u)
            g['grades']['course_units'] = units
            grades.append(g)
        self.write(json_util.dumps(grades))

class GradesForCourseAndTermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        user_doc, usos_doc = yield self.get_parameters()

        grade_doc = yield self.db[constants.COLLECTION_GRADES].find_one(
                {constants.USER_ID: ObjectId(user_doc[constants.USER_ID]),
                 constants.COURSE_ID: course_id,
                 constants.TERM_ID: term_id})

        if not grade_doc:
            pass    # TODO: return json with custom message

        self.write(json_util.dumps(grade_doc))
