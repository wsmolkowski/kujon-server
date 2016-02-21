import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from staracommon import constants
import pprint

class GradesForUserApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()
        grades = []

        # get class_types
        classtypes = {}
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: parameters[constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        cursor = self.db[constants.COLLECTION_GRADES].find({constants.USER_ID: ObjectId(parameters[constants.ID])},
                            ('grades', constants.TERM_ID, constants.COURSE_ID, 'course_name')).sort([(constants.TERM_ID, -1)])

        while (yield cursor.fetch_next):
            grades_for_course_and_term = cursor.next_object()
            grades_for_course_and_term.pop(constants.ID)
            grades_for_course_and_term['course_name'] = grades_for_course_and_term['course_name']['pl']

            units = {}
            for unit in grades_for_course_and_term['grades']['course_units_grades']:
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

            new_grades = []
            if len(units) > 0: # oceny czeciowe
                grades_for_course_and_term['grades']['course_units'] = units
                for egzam in grades_for_course_and_term['grades']['course_units_grades']:
                    for termin in grades_for_course_and_term['grades']['course_units_grades'][egzam]:
                        elem = grades_for_course_and_term['grades']['course_units_grades'][egzam][termin]
                        elem['class_type'] = units[int(egzam)]['classtype_id']
                        elem['value_description'] = elem['value_description']['pl']
                        new_grades.append(elem)
                grades_for_course_and_term['grades'] = new_grades
                grades.append(grades_for_course_and_term)
            else: # ocena koncowa bez czesciowych
                for egzam in grades_for_course_and_term['grades']['course_grades']:
                    elem = grades_for_course_and_term['grades']['course_grades'][egzam]
                    elem['value_description'] = elem['value_description']['pl']
                    elem['class_type'] = constants.GRADE_FINAL
                    new_grades.append(elem)
                grades_for_course_and_term['grades'] = new_grades
                grades.append(grades_for_course_and_term)

        if not grades:
            self.error("Please hold on we are looking your grades.")
        else:
            self.success(grades)


class GradesForCourseAndTermApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        parameters = yield self.get_parameters()

        pipeline = {constants.USER_ID: ObjectId(parameters[constants.ID]), constants.COURSE_ID: course_id,
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
            self.error("We could not find grades for course_id: {0} term_id {1}.".format(course_id, term_id))
        else:
            # self.success(grades)
            self.__write_json(pprint(grades))

