# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants


class GradesForUserApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        grades = list()

        # get class_types
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find(
            {constants.USOS_ID: parameters[constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        cursor = self.db[constants.COLLECTION_GRADES].find({constants.USER_ID: ObjectId(parameters[constants.MONGO_ID])},
                                                           ('grades', constants.TERM_ID, constants.COURSE_ID,
                                                            'course_name')).sort([(constants.TERM_ID, -1)])
        new_grades = []

        while (yield cursor.fetch_next):
            grades_courseedition = cursor.next_object()
            grades_courseedition.pop(constants.MONGO_ID)
            grades_courseedition['course_name'] = grades_courseedition['course_name']['pl']

            # if there is no grades -> pass
            if len(grades_courseedition['grades']['course_grades'])==0 and len(grades_courseedition['grades']['course_units_grades'])==0:
                continue

            units = {}
            for unit in grades_courseedition['grades']['course_units_grades']:
                pipeline = [{'$match': {'unit_id': int(unit), constants.USOS_ID: parameters[constants.USOS_ID]}}, {
                    '$lookup': {'from': 'courses_classtypes', 'localField': 'classtype_id', 'foreignField': 'id',
                                'as': 'courses_classtypes'}}]
                unit_coursor = self.db[constants.COLLECTION_COURSES_UNITS].aggregate(pipeline)
                u = yield unit_coursor.to_list(None)
                for elem in u:
                    unit_id = elem['unit_id']
                    elem.pop('unit_id')
                    elem.pop('created_time')
                    elem.pop('update_time')
                    elem.pop('term_id')
                    elem.pop('usos_id')
                    elem.pop('courses_classtypes')
                    elem.pop('groups')
                    elem['classtype_id'] = classtypes[(elem['classtype_id'])]
                    units[unit_id] = elem

            if len(units) > 0:  # oceny czeciowe
                grades_courseedition['grades']['course_units'] = units
                for egzam in grades_courseedition['grades']['course_units_grades']:
                    for termin in grades_courseedition['grades']['course_units_grades'][egzam]:
                        elem = grades_courseedition['grades']['course_units_grades'][egzam][termin]
                        if int(egzam) in units:
                            elem['class_type'] = units[int(egzam)]['classtype_id']
                        else:
                            elem['class_type'] = None
                        elem['value_description'] = elem['value_description']['pl']
                        elem[constants.COURSE_ID] = grades_courseedition[constants.COURSE_ID]
                        elem['course_name'] = grades_courseedition['course_name']
                        elem['term_id'] = grades_courseedition['term_id']
                        new_grades.append(elem)
            else:  # ocena koncowa bez czesciowych
                for egzam in grades_courseedition['grades']['course_grades']:
                    elem = grades_courseedition['grades']['course_grades'][egzam]
                    elem['value_description'] = elem['value_description']['pl']
                    elem['class_type'] = constants.GRADE_FINAL
                    elem[constants.COURSE_ID] = grades_courseedition[constants.COURSE_ID]
                    elem['course_name'] = grades_courseedition['course_name']
                    elem['term_id'] = grades_courseedition['term_id']
                    new_grades.append(elem)

        self.success(new_grades)


class GradesForCourseAndTermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        parameters = yield self.get_parameters()

        pipeline = {constants.USER_ID: ObjectId(parameters[constants.MONGO_ID]), constants.COURSE_ID: course_id,
                    constants.TERM_ID: term_id}
        limit_fields = ('course_name', 'course_id', 'grades')

        classtypes = {}
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: parameters[
            constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        grades = yield self.db[constants.COLLECTION_GRADES].find_one(pipeline, limit_fields)
        units = {}
        if grades and len(grades) > 0:
            for unit in grades['grades']['course_units_grades']:
                # TODO: to refactor - join data for 2 usoses and data not connected well
                pipeline = [{'$match': {'unit_id': int(unit)}}, {
                    '$lookup': {'from': 'courses_classtypes', 'localField': 'classtype_id', 'foreignField': 'id',
                                'as': 'courses_classtypes'}}]
                unit_coursor = self.db[constants.COLLECTION_COURSES_UNITS].aggregate(pipeline)
                u = yield unit_coursor.to_list(None)
                for elem in u:
                    unit_id = elem['unit_id']
                    elem.pop('unit_id')
                    elem['classtype_id'] = classtypes[(elem['classtype_id'])]
                    units[unit_id] = elem
            if len(units) > 0:
                grades['grades']['course_units'] = units
                del grades['grades']['course_grades']
            else:
                del grades['grades']['course_units_grades']

        if not grades:
            self.error("Nie ma ocen dla przedmiotu {0} i semestru {1}.".format(course_id, term_id))
        else:
            self.success(grades)
