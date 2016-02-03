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
            grades_for_course_and_term = cursor.next_object()
            units = {}
            for unit in grades_for_course_and_term['grades']['course_units_grades']:
                # TODO: to refactor - join data for 2 usoses and data not connected well
                pipeline = [{'$match': {'unit_id': int(unit)}},{'$lookup': {'from': 'courses_classtypes', 'localField': 'classtype_id', 'foreignField': 'id', 'as': 'courses_classtypes'}}]
                unit_coursor = self.db[constants.COLLECTION_COURSES_UNITS].aggregate(pipeline)
                u = yield unit_coursor.to_list(None)
                for elem in u:
                    unit_id = elem['unit_id']
                    elem.pop('unit_id')
                    units[unit_id] = elem
            if len(units) > 0:
                grades_for_course_and_term['grades']['course_units'] = units
                del grades_for_course_and_term['grades']['course_grades']
            else:
                del grades_for_course_and_term['grades']['course_units_grades']
            grades.append(grades_for_course_and_term)
        self.write(json_util.dumps(grades))

class GradesForCourseAndTermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        user_doc, usos_doc = yield self.get_parameters()
        grade_doc = []
        pipeline = {constants.USER_ID: ObjectId(user_doc[constants.USER_ID]),constants.COURSE_ID: course_id, constants.TERM_ID: term_id}
        grades = yield self.db[constants.COLLECTION_GRADES].find_one(pipeline)
        units = []
        if len(grades) > 0:
            for unit in grades['grades']['course_units_grades']:
                # TODO: to refactor - join data for 2 usoses and data not connected well
                pipeline = [{'$match': {'unit_id': int(unit)}},{'$lookup': {'from': 'courses_classtypes', 'localField': 'classtype_id', 'foreignField': 'id', 'as': 'courses_classtypes'}}]
                unit_coursor = self.db[constants.COLLECTION_COURSES_UNITS].aggregate(pipeline)
                u = yield unit_coursor.to_list(None)
                for elem in u:
                    unit_id = elem['unit_id']
                    elem.pop('unit_id')
                    units[unit_id] = elem
            if len(units) > 0:
                grades['grades']['course_units'] = units
                del grades['grades']['course_grades']
            else:
                del grades['grades']['course_units_grades']


        self.write(json_util.dumps(grades))
