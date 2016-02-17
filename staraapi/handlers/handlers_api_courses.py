import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from staracommon import constants

LIMIT_FIELDS = ('is_currently_conducted', 'bibliography', 'name', constants.FACULTY_ID, 'assessment_criteria',
                constants.COURSE_ID, 'homepage_url', 'lang_id', 'learning_outcomes', 'description')


class CoursesApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id):

        parameters = yield self.get_parameters()

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one({constants.COURSE_ID: course_id,
                                                                           constants.USOS_ID: parameters[
                                                                               constants.USOS_ID]}, LIMIT_FIELDS)

        if not course_doc:
            self.fail("We could not find for you course with course_id: {0}.".format(course_id))
        else:
            # change true to TAK
            if course_doc['is_currently_conducted'] == True:
                course_doc['is_currently_conducted'] = 'TAK'
            else:
                course_doc['is_currently_conducted'] = 'NIE'

            # change faculty_id to faculty name
            LIMIT_FIELDS_FACULTY = (
            constants.FACULTY_ID, 'logo_urls', 'name', 'postal_address', 'homepage_url', 'phone_numbers')
            fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: course_doc[
                constants.FACULTY_ID],
                                                                              constants.USOS_ID: parameters[
                                                                                  constants.USOS_ID]}, LIMIT_FIELDS_FACULTY)
            course_doc.pop(constants.FACULTY_ID)
            course_doc[constants.FACULTY_ID] = fac_doc

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

            # get courses_classtypes
            classtypes = {}
            cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: parameters[
                constants.USOS_ID]})
            while (yield cursor.fetch_next):
                ct = cursor.next_object()
                classtypes[ct['id']] = ct['name']['pl']


            # group terms by academic years
            courses_new = {}
            for term in course_doc['course_editions']:
                year = term[0:4]
                if not year in courses_new:
                    courses_new[year] = []
                for course in course_doc['course_editions'][term]:
                    courses_new[year].append(course)

            # add groups to courses
            courses_with_groups = {}
            LIMIT_FIELDS_GROUPS = ('class_type_id','group_number','course_unit_id')
            for year in courses_new:
                if not year in courses_with_groups:
                    courses_with_groups[year] = []
                course_new = []
                for course in courses_new[year]:
                    cursor = self.db[constants.COLLECTION_GROUPS].find(
                        {constants.COURSE_ID: course[constants.COURSE_ID],
                         constants.TERM_ID: course[constants.TERM_ID],
                         constants.USOS_ID: parameters[constants.USOS_ID]},
                          LIMIT_FIELDS_GROUPS
                        )
                    course['groups'] = []
                    while (yield cursor.fetch_next):
                        group = cursor.next_object()
                        group.pop("_id")
                        group['class_type_id'] = classtypes[group['class_type_id']] # changing class_type_id to name
                        course['groups'].append(group)
                    courses_with_groups[year].append(course)

            self.success(courses_with_groups)