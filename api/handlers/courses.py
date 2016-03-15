# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants
from commons.usosutils import usoshelper

LIMIT_FIELDS = ('is_currently_conducted', 'bibliography', 'name', constants.FACULTY_ID, 'assessment_criteria',
                constants.COURSE_ID, 'homepage_url', 'lang_id', 'learning_outcomes', 'description')
LIMIT_FIELDS_COURSE_EDITION = ('lecturers', 'coordinators', 'participants', 'course_units_ids', 'grades')
LIMIT_FIELDS_GROUPS = ('class_type_id', 'group_number', 'course_unit_id')
LIMIT_FIELDS_FACULTY = (constants.FACULTY_ID, 'logo_urls', 'name', 'postal_address', 'homepage_url', 'phone_numbers')
LIMIT_FIELDS_TERMS = ('name', 'start_date', 'end_date', 'finish_date')


class CourseEditionApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):

        parameters = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one({constants.COURSE_ID: course_id,
                                                                           constants.USOS_ID: parameters[
                                                                               constants.USOS_ID]}, LIMIT_FIELDS)

        if not course_doc:
            self.error("Nie znaleźliśmy kursu.")
            return

        # change int to value
        course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
            course_doc['is_currently_conducted'])

        # get courses_classtypes
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: parameters[
            constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        # change faculty_id to faculty name
        fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: course_doc[
            constants.FACULTY_ID], constants.USOS_ID: parameters[constants.USOS_ID]}, LIMIT_FIELDS_FACULTY)
        course_doc.pop(constants.FACULTY_ID)
        course_doc[constants.FACULTY_ID] = fac_doc
        course_doc['fac_id']['name'] = course_doc['fac_id']['name']['pl']

        # get information about course_edition
        course_edition_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
            {constants.COURSE_ID: course_id, constants.USOS_ID: parameters[constants.USOS_ID],
             constants.TERM_ID: term_id}, LIMIT_FIELDS_COURSE_EDITION)
        if not course_edition_doc:
            self.error("Bląd podczas pobierania course_edition.")
            return

        # sort participant
        if 'participants' in course_doc:
            course_doc['participants'] = sorted(course_edition_doc['participants'], key=lambda k: k['last_name'])
        else:
            pass

        # make lecurers uniqe list
        course_doc['lecturers'] = list({item["id"]: item for item in course_edition_doc['lecturers']}.values())

        course_doc['coordinators'] = course_edition_doc['coordinators']
        course_doc['course_units_ids'] = course_edition_doc['course_units_ids']
        if 'grades' in course_doc:
            course_doc['grades'] = course_edition_doc['grades']

        groups = list()
        # get information about group
        if course_doc['course_units_ids']:
            for unit in course_doc['course_units_ids']:
                # groups
                group_doc = yield self.db[constants.COLLECTION_GROUPS].find_one(
                    {constants.COURSE_ID: course_id, constants.USOS_ID: parameters[constants.USOS_ID],
                     constants.TERM_ID: term_id, 'course_unit_id': int(unit)}, LIMIT_FIELDS_GROUPS)
                if not group_doc:
                    continue
                else:
                    group_doc['class_type'] = classtypes[group_doc['class_type_id']]
                    del (group_doc['class_type_id'])
                    groups.append(group_doc)
        course_doc['groups'] = groups

        # terms
        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one(
            {constants.USOS_ID: parameters[constants.USOS_ID],
             constants.TERM_ID: term_id}, LIMIT_FIELDS_TERMS)
        if not term_doc:
            pass
        else:
            term_doc['name'] = term_doc['name']['pl']
            course_doc['term'] = term_doc

        self.success(course_doc)


class CoursesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id):

        parameters = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one({constants.COURSE_ID: course_id,
                                                                           constants.USOS_ID: parameters[
                                                                               constants.USOS_ID]}, LIMIT_FIELDS)

        if not course_doc:
            self.error("Nie znaleźliśmy danych kursu: {0}.".format(course_id))
            return

        # change id to value
        course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
            course_doc['is_currently_conducted'])

        # change faculty_id to faculty name
        fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: course_doc[
            constants.FACULTY_ID], constants.USOS_ID: parameters[constants.USOS_ID]}, LIMIT_FIELDS_FACULTY)
        course_doc.pop(constants.FACULTY_ID)
        course_doc[constants.FACULTY_ID] = fac_doc
        course_doc['fac_id']['name'] = course_doc['fac_id']['name']['pl']

        self.success(course_doc)


class CoursesEditionsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.MONGO_ID])},
            ('course_editions',)
        )

        if not course_doc:
            self.error("Poczekaj szukamy przedmiotów.")
            return

        # get courses_classtypes
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: parameters[
            constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        # get terms
        terms = list()
        for term in course_doc['course_editions']:
            year = {
                'term': term,
                'term_data': course_doc['course_editions'][term]
            }
            terms.append(year)

        # add groups to courses
        courses = list()
        for term in terms:
            for course in term['term_data']:
                cursor = self.db[constants.COLLECTION_GROUPS].find(
                    {constants.COURSE_ID: course[constants.COURSE_ID],
                     constants.TERM_ID: course[constants.TERM_ID],
                     constants.USOS_ID: parameters[constants.USOS_ID]},
                    LIMIT_FIELDS_GROUPS
                )
                groups = list()
                while (yield cursor.fetch_next):
                    group = cursor.next_object()
                    group['class_type_id'] = classtypes[group['class_type_id']]  # changing class_type_id to name
                    groups.append(group)
                course['groups'] = groups
                course['course_name'] = course['course_name']['pl']
                del course['course_units_ids']
                courses.append(course)

        self.success(courses)
