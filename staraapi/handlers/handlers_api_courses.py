import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from staracommon import constants

LIMIT_FIELDS = ('is_currently_conducted', 'bibliography', 'name', constants.FACULTY_ID, 'assessment_criteria',
                constants.COURSE_ID, 'homepage_url', 'lang_id', 'learning_outcomes', 'description')

LIMIT_FIELDS_GROUPS = ('class_type_id', 'group_number', 'course_unit_id')


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
                                                                                  constants.USOS_ID]},
                                                                             LIMIT_FIELDS_FACULTY)
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
            ('course_editions',)
        )

        if not course_doc:
            self.error("Please hold on we are looking your courses.")

        # get courses_classtypes
        classtypes = {}
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: parameters[
            constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        terms = []
        for term in course_doc['course_editions']:

            year = {
                'term': term,
                'term_data': course_doc['course_editions'][term]
            }
            terms.append(year)

        # add groups to courses
        term_counter = -1       # web client tab navigation
        results = []
        for term in terms:
            term_counter += 1
            courses = []
            for course in term['term_data']:
                cursor = self.db[constants.COLLECTION_GROUPS].find(
                    {constants.COURSE_ID: course[constants.COURSE_ID],
                     constants.TERM_ID: course[constants.TERM_ID],
                     constants.USOS_ID: parameters[constants.USOS_ID]},
                    LIMIT_FIELDS_GROUPS
                )
                groups = []
                while (yield cursor.fetch_next):
                    group = cursor.next_object()
                    group['class_type_id'] = classtypes[group['class_type_id']]  # changing class_type_id to name
                    groups.append(group)
                course['groups'] = groups
                courses.append(course)

            results.append({
                'term': term['term'],
                'term_counter': term_counter,
                'term_data': courses
            })
        self.success(results)
