# coding=UTF-8

import logging
from collections import OrderedDict
from datetime import date, timedelta, datetime

from bson.objectid import ObjectId
from tornado import gen

from commons import constants, settings
from commons.errors import ApiError, UsosClientError
from commons.mixins.UsosMixin import UsosMixin
from commons.usosutils import usoshelper
from database import DatabaseHandler

LIMIT_FIELDS = (
    'is_currently_conducted', 'bibliography', constants.COURSE_NAME, constants.FACULTY_ID, 'assessment_criteria',
    constants.COURSE_ID, 'homepage_url', 'lang_id', 'learning_outcomes', 'description')
LIMIT_FIELDS_COURSE_EDITION = ('lecturers', 'coordinators', 'participants', 'course_units_ids', 'grades')
LIMIT_FIELDS_GROUPS = ('class_type_id', 'group_number', 'course_unit_id')
LIMIT_FIELDS_FACULTY = (constants.FACULTY_ID, 'logo_urls', 'name', 'postal_address', 'homepage_url', 'phone_numbers')
LIMIT_FIELDS_TERMS = ('name', 'start_date', 'end_date', 'finish_date')
LIMIT_FIELDS_USER = (
    'first_name', 'last_name', 'titles', 'email_url', constants.ID, constants.HAS_PHOTO, 'staff_status', 'room',
    'office_hours', 'employment_positions', 'course_editions_conducted', 'interests', 'homepage_url')
LIMIT_FIELDS_PROGRAMMES = (
    'name', 'mode_of_studies', 'level_of_studies', 'programme_id', 'duration', 'description', 'faculty')
TERM_LIMIT_FIELDS = ('name', 'end_date', 'finish_date', 'start_date', 'name', 'term_id')
USER_INFO_LIMIT_FIELDS = (
    'first_name', 'last_name', constants.ID, 'student_number', 'student_status', 'has_photo', 'student_programmes',
    'user_type', constants.HAS_PHOTO, 'staff_status', 'employment_positions', 'room', 'course_editions_conducted',
    'titles', 'office_hours', 'homepage_url', 'has_email', 'email_url', 'sex', 'user_id')


class ApiDaoHandler(DatabaseHandler, UsosMixin):
    def do_refresh(self):
        if self.request.headers.get(constants.MOBILE_X_HEADER_REFRESH, False):
            return True
        return False

    @gen.coroutine
    def api_courses_editions(self):
        user_id = ObjectId(self.user_doc[constants.MONGO_ID])

        pipeline = {constants.USER_ID: user_id}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_COURSES_EDITIONS, pipeline)

        courses_editions_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            pipeline, (constants.COURSE_EDITIONS,))

        if not courses_editions_doc:
            courses_editions_doc = yield self.usos_courses_editions()
            yield self.insert(constants.COLLECTION_COURSES_EDITIONS, courses_editions_doc)

        raise gen.Return(courses_editions_doc)

    @gen.coroutine
    def api_course_edition(self, course_id, term_id, fetch_participants, finish=True):
        pipeline = {constants.COURSE_ID: course_id,
                    constants.TERM_ID: term_id,
                    constants.USOS_ID: self.user_doc[constants.USOS_ID],
                    constants.USER_ID: self.user_doc[constants.MONGO_ID]}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_COURSE_EDITION, pipeline)

        course_edition_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(pipeline)

        if not course_edition_doc:
            try:
                course_edition_doc = yield self.usos_course_edition(course_id, term_id, fetch_participants)
                yield self.insert(constants.COLLECTION_COURSE_EDITION, course_edition_doc)
            except UsosClientError, ex:
                raise self.exc(ex, finish=finish)

        raise gen.Return(course_edition_doc)

    @gen.coroutine
    def api_course_term(self, course_id, term_id, user_id=None):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        pipeline = {constants.COURSE_ID: course_id,
                    constants.USOS_ID: usos_doc[constants.USOS_ID],
                    constants.USER_ID: self.user_doc[constants.MONGO_ID]}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            try:
                course_doc = yield self.usos_course(course_id)

                yield self.insert(constants.COLLECTION_COURSES, course_doc)
            except Exception, ex:
                logging.exception(ex)
                raise ApiError("Nie znaleźliśmy kursu", course_id)

        course_doc[constants.TERM_ID] = term_id

        course_edition_doc = yield self.api_course_edition(course_id, term_id, fetch_participants=False)

        if not course_edition_doc:
            raise ApiError("Nie znaleźliśmy edycji kursu", (course_id, term_id))

        if not user_id:
            user_info_doc = yield self.api_user_info()
        else:
            user_info_doc = yield self.api_user_info(user_id)

        if not user_info_doc:
            raise ApiError("Błąd podczas pobierania danych użytkownika", (course_id, term_id))

        # checking if user is on this course, so have access to this course # FIXME
        if 'participants' in course_edition_doc and constants.ID in user_info_doc:
            # sort participants
            course_doc['participants'] = sorted(course_edition_doc['participants'], key=lambda k: k['last_name'])

            participants = course_doc['participants']
            for participant in course_doc['participants']:
                if participant[constants.USER_ID] == user_info_doc[constants.ID]:
                    participants.remove(participant)
                    break

            course_doc['participants'] = participants

        # change int to value
        course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
            course_doc['is_currently_conducted'])

        classtypes = yield self.get_classtypes()


        # make lecturers unique list
        course_doc['lecturers'] = list({item["id"]: item for item in course_edition_doc['lecturers']}.values())

        course_doc['coordinators'] = course_edition_doc['coordinators']
        course_doc['course_units_ids'] = course_edition_doc['course_units_ids']

        if 'grades' in course_doc:
            course_doc['grades'] = course_edition_doc['grades']

        groups = list()
        # get information about group
        if course_doc['course_units_ids']:
            for unit in course_doc['course_units_ids']:
                try:
                    group_doc = yield self.api_group(course_id, term_id, int(unit), finish=False)
                    if group_doc:
                        group_doc[constants.CLASS_TYPE] = classtypes[group_doc['class_type_id']]
                        del (group_doc['class_type_id'])
                        groups.append(group_doc)
                except Exception, ex:
                    yield self.exc(ex, finish=False)
        course_doc['groups'] = groups

        term_doc = yield self.api_term(term_id)

        if term_doc:
            course_doc['term'] = term_doc

        # change faculty_id to faculty name
        faculty_doc = yield self.api_faculty(course_doc[constants.FACULTY_ID])
        course_doc[constants.FACULTY_ID] = {constants.FACULTY_ID: faculty_doc[constants.FACULTY_ID],
                                            constants.FACULTY_NAME: faculty_doc[constants.FACULTY_NAME]}

        raise gen.Return(course_doc)

    @gen.coroutine
    def api_course(self, course_id):

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            try:
                course_doc = yield self.usos_course(course_id)
            except UsosClientError, ex:
                yield self.exc(ex, finish=True)
                raise gen.Return(None)

            yield self.insert(constants.COLLECTION_COURSES, course_doc)

            # change id to value
            course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
                course_doc['is_currently_conducted'])

            # change faculty_id to faculty name
            faculty_doc = yield self.api_faculty(course_doc[constants.FACULTY_ID])
            if not faculty_doc:
                faculty_doc = yield self.usos_faculty(course_doc[constants.FACULTY_ID])
            course_doc[constants.FACULTY_ID] = {constants.FACULTY_ID: faculty_doc[constants.FACULTY_ID],
                                                constants.FACULTY_NAME: faculty_doc[constants.FACULTY_NAME]}

            if not course_doc:
                raise ApiError("Nie znaleźliśmy danych kursu.", course_id)

        raise gen.Return(course_doc)

    @gen.coroutine
    def api_courses(self):
        courses_editions_doc = yield self.api_courses_editions()

        if not courses_editions_doc:
            raise ApiError("Poczekaj szukamy przedmiotów")

        classtypes = yield self.get_classtypes()

        def classtype_name(key_id):
            for key, name in classtypes.items():
                if str(key_id) == str(key):
                    return name
            return key_id

        # get terms
        terms = list()
        for term in courses_editions_doc[constants.COURSE_EDITIONS]:
            term_with_courses = {
                'term': term,
                'term_data': courses_editions_doc[constants.COURSE_EDITIONS][term]
            }
            terms.append(term_with_courses)

        # add groups to courses
        courses = list()
        for term in terms:
            for course in term['term_data']:
                cursor = self.db[constants.COLLECTION_GROUPS].find(
                    {constants.COURSE_ID: course[constants.COURSE_ID],
                     constants.TERM_ID: course[constants.TERM_ID],
                     constants.USOS_ID: self.user_doc[constants.USOS_ID]},
                    LIMIT_FIELDS_GROUPS
                )
                groups = list()
                while (yield cursor.fetch_next):
                    group = cursor.next_object()
                    group['class_type'] = classtype_name(group['class_type_id'])  # changing class_type_id to name
                    group.pop('class_type_id')
                    groups.append(group)
                course['groups'] = groups
                course[constants.COURSE_NAME] = course[constants.COURSE_NAME]['pl']
                del course['course_units_ids']
                courses.append(course)

        raise gen.Return(courses)

    @gen.coroutine
    def api_courses_by_term(self):

        courses_edition = yield self.api_courses()

        # grouping grades by term
        courses = dict()
        terms = list()
        for course in courses_edition:
            if course[constants.TERM_ID] not in courses:
                courses[course[constants.TERM_ID]] = list()
                terms.append(course[constants.TERM_ID])
            courses[course[constants.TERM_ID]].append(course)

        # get course in order in order_keys as dictionary and reverse sort
        terms_by_order = yield self.get_terms_with_order_keys(terms)
        terms_by_order = OrderedDict(sorted(terms_by_order.items(), reverse=True))
        courses_sorted_by_term = list()
        for order_key in terms_by_order:
            courses_sorted_by_term.append({terms_by_order[order_key]: courses[terms_by_order[order_key]]})

        raise gen.Return(courses_sorted_by_term)

    @gen.coroutine
    def api_grades(self):
        # get class_types
        classtypes = yield self.get_classtypes()

        pipeline = {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])}
        limit_fields = ('grades', constants.TERM_ID, constants.COURSE_ID, constants.COURSE_NAME)

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_COURSE_EDITION, pipeline)
            yield self.api_courses_editions()

        cursor = self.db[constants.COLLECTION_COURSE_EDITION].find(pipeline, limit_fields).sort(
            [(constants.TERM_ID, -1)])

        grades = yield cursor.to_list(None)

        grades_sorted = list()
        for grade in grades:
            grade.pop(constants.MONGO_ID)

            # if there is no grades -> pass
            if not 'grades' in grade or not 'course_grades' in grade['grades'] or 'course_units_grades' not in grade['grades'] \
                    or (len(grade['grades']['course_grades']) == 0 and len(grade['grades']['course_units_grades']) == 0):
                continue

            units = {}
            for unit in grade['grades']['course_units_grades']:
                pipeline = [{'$match': {'unit_id': int(unit), constants.USOS_ID: self.user_doc[constants.USOS_ID]}}, {
                    '$lookup': {'from': 'courses_classtypes', 'localField': 'classtype_id', 'foreignField': 'id',
                                'as': 'courses_classtypes'}}]
                unit_coursor = self.db[constants.COLLECTION_COURSES_UNITS].aggregate(pipeline)
                u = yield unit_coursor.to_list(None)
                for elem in u:
                    unit_id = elem[constants.UNIT_ID]
                    elem.pop(constants.UNIT_ID)
                    elem.pop(constants.CREATED_TIME)
                    elem.pop(constants.UPDATE_TIME)
                    elem.pop(constants.TERM_ID)
                    elem.pop(constants.USOS_ID)
                    elem.pop('courses_classtypes')
                    elem.pop('groups')
                    elem[constants.CLASS_TYPE_ID] = classtypes[(elem[constants.CLASS_TYPE_ID])]
                    units[unit_id] = elem

            if len(units) > 0:  # partial grades
                grade['grades']['course_units'] = units
                for egzam in grade['grades']['course_units_grades']:
                    for termin in grade['grades']['course_units_grades'][egzam]:
                        elem = grade['grades']['course_units_grades'][egzam][termin]
                        if int(egzam) in units:
                            elem[constants.CLASS_TYPE] = units[int(egzam)][constants.CLASS_TYPE_ID]
                        else:
                            elem[constants.CLASS_TYPE] = None
                        elem[constants.VALUE_DESCRIPTION] = elem[constants.VALUE_DESCRIPTION]['pl']
                        elem[constants.COURSE_ID] = grade[constants.COURSE_ID]
                        elem[constants.COURSE_NAME] = grade[constants.COURSE_NAME]
                        elem[constants.TERM_ID] = grade[constants.TERM_ID]
                        grades_sorted.append(elem)
            else:  # final grade no partials
                for egzam in grade['grades']['course_grades']:
                    elem = grade['grades']['course_grades'][egzam]
                    elem[constants.VALUE_DESCRIPTION] = elem[constants.VALUE_DESCRIPTION]['pl']
                    elem[constants.CLASS_TYPE] = constants.GRADE_FINAL
                    elem[constants.COURSE_ID] = grade[constants.COURSE_ID]
                    elem[constants.COURSE_NAME] = grade[constants.COURSE_NAME]
                    elem[constants.TERM_ID] = grade[constants.TERM_ID]
                    grades_sorted.append(elem)

        raise gen.Return(grades_sorted)

    @gen.coroutine
    def api_grades_byterm(self):

        new_grades = yield self.api_grades()

        # grouping grades by term
        grades = dict()
        terms = list()
        for grade in new_grades:
            if grade[constants.TERM_ID] not in grades:
                grades[grade[constants.TERM_ID]] = list()
                terms.append(grade[constants.TERM_ID])
            grades[grade[constants.TERM_ID]].append(grade)

        # sort grades in order of terms by order_keys descending
        terms_by_order = yield self.get_terms_with_order_keys(terms)
        terms_by_order = OrderedDict(sorted(terms_by_order.items(), reverse=True))
        grades_sorted_by_term = list()
        for order_key in terms_by_order:
            grades_sorted_by_term.append({terms_by_order[order_key]: grades[terms_by_order[order_key]]})

        raise gen.Return(grades_sorted_by_term)

    @gen.coroutine
    def api_lecturers(self):
        courses = {}
        lecturers_returned = {}

        courses_editions_doc = yield self.api_courses_editions()

        if courses_editions_doc:

            for term in courses_editions_doc[constants.COURSE_EDITIONS]:
                for course in courses_editions_doc[constants.COURSE_EDITIONS][term]:
                    courses[course[constants.COURSE_ID]] = course

            for course in courses:
                course_edition_doc = yield self.api_course_edition(course, courses[course][constants.TERM_ID],
                                                                   fetch_participants=True, finish=False)

                if not course_edition_doc:
                    continue

                for lecturer in course_edition_doc[constants.LECTURERS]:
                    lecturer_id = lecturer[constants.USER_ID]
                    lecturers_returned[lecturer_id] = lecturer

        lecturers_returned = lecturers_returned.values()

        raise gen.Return(lecturers_returned)

    @gen.coroutine
    def api_lecturer(self, user_info_id):

        user_info = yield self.api_user_info(user_info_id)

        if not user_info:
            raise ApiError("Poczekaj szukamy informacji o nauczycielu.", user_info_id)

        raise gen.Return(user_info)

    @gen.coroutine
    def api_programmes(self):

        user_info = yield self.api_user_info()

        if not user_info:
            raise ApiError("Brak danych o użytkowniku.")

        programmes = []
        for program in user_info['student_programmes']:
            result = yield self.api_programme(program['programme']['id'], finish=False)
            if result:
                program['programme']['mode_of_studies'] = result['mode_of_studies']
                program['programme']['level_of_studies'] = result['level_of_studies']
                program['programme']['duration'] = result['duration']
                program['programme']['name'] = result['name']
                programmes.append(program)
            else:
                yield self.exc(ApiError("Nie znaleziono programu", program['programme']['id']), finish=False)

        raise gen.Return(programmes)

    @gen.coroutine
    def api_programme(self, programme_id, finish=True):
        pipeline = {constants.PROGRAMME_ID: programme_id}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_PROGRAMMES, pipeline)

        programme_doc = yield self.db[constants.COLLECTION_PROGRAMMES].find_one(pipeline, LIMIT_FIELDS_PROGRAMMES)

        if not programme_doc:
            try:
                programme_doc = yield self.usos_programme(programme_id)
                yield self.insert(constants.COLLECTION_PROGRAMMES, programme_doc)
            except UsosClientError, ex:
                raise self.exc(ex, finish=finish)

        raise gen.Return(programme_doc)

    @gen.coroutine
    def api_tt(self, given_date):
        try:
            given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))
            monday = given_date - timedelta(days=(given_date.weekday()) % 7)
        except Exception, ex:
            self.error("Niepoprawny format daty: RRRR-MM-DD.")
            yield self.exc(ex)

        user_id = ObjectId(self.user_doc[constants.MONGO_ID])

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_TT, {constants.USER_ID: user_id})

        # fetch TT from mongo
        tt_doc = yield self.db[constants.COLLECTION_TT].find_one({constants.USER_ID: user_id,
                                                                  constants.TT_STARTDATE: str(monday)})
        if not tt_doc:

            try:
                tt_doc = yield self.time_table(monday)
                yield self.insert(constants.COLLECTION_TT, tt_doc)
            except Exception, ex:
                yield self.exc(ex, finish=False)
                raise gen.Return(None)

        # remove english names
        for t in tt_doc['tts']:
            t['name'] = t['name']['pl']
            t[constants.COURSE_NAME] = t[constants.COURSE_NAME]['pl']
            t['building_name'] = t['building_name']['pl']
            if t['type'] == 'classgroup':
                t['type'] = 'zajęcia'
            elif t['type'] == 'exam':
                t['type'] = 'egzamin'

        # add lecturer information
        lecturer_keys = ['id', 'first_name', 'last_name', 'titles']
        for tt in tt_doc['tts']:
            for lecturer in tt['lecturer_ids']:
                lecturer_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
                    {constants.ID: str(lecturer)}, lecturer_keys)
                if not lecturer_info:
                    lecturer_info = yield self.api_user_info(str(lecturer))
                    lecturer_info = dict([(key, lecturer_info[key]) for key in lecturer_keys])
                    if not lecturer_info:
                        exception = ApiError("Błąd podczas pobierania nauczyciela (%r) dla planu.".format(lecturer))
                        yield self.exc(exception, finish=False)
                tt['lecturers'] = list()
                tt['lecturers'].append(lecturer_info)
            del (tt['lecturer_ids'])
        raise gen.Return(tt_doc['tts'])

    @gen.coroutine
    def api_term(self, term_id):
        pipeline = {constants.TERM_ID: term_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_TERMS, pipeline)

        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one(pipeline, TERM_LIMIT_FIELDS)

        if not term_doc:
            term_doc = yield self.usos_term(term_id)
            yield self.insert(constants.COLLECTION_TERMS, term_doc)

        today = date.today()
        end_date = datetime.strptime(term_doc['finish_date'], "%Y-%m-%d").date()
        if today <= end_date:
            term_doc['active'] = True
        else:
            term_doc['active'] = False

        raise gen.Return(term_doc)

    @gen.coroutine
    def api_terms(self):

        terms = dict()
        terms_list = list()
        terms_ordered = list()

        if self.do_refresh():
            # pobieranie zaimplmentowane już w api_courses_editions
            pass

        courses_editions_doc = yield self.api_courses_editions()

        if courses_editions_doc:
            for term_id in courses_editions_doc[constants.COURSE_EDITIONS]:
                term_doc = yield self.api_term(term_id)
                terms[term_id] = term_doc
                terms_list.append(term_id)

            # order terms from newset
            terms_by_order = yield self.get_terms_with_order_keys(terms)
            terms_by_order = OrderedDict(sorted(terms_by_order.items(), reverse=True))
            for order_key in terms_by_order:
                terms_ordered.append(terms[terms_by_order[order_key]])

        raise gen.Return(terms_ordered)

    @gen.coroutine
    def api_user_info(self, user_id=None):

        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        if not user_id:
            pipeline = {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID]), constants.USOS_ID: usos_doc[constants.USOS_ID]}
        else:
            pipeline = {constants.ID: str(user_id), constants.USOS_ID: usos_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_USERS_INFO, pipeline)

        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(pipeline, USER_INFO_LIMIT_FIELDS)

        if not user_info_doc:
            user_info_doc = yield self.usos_user_info(user_id)
            if not user_info_doc:
                raise ApiError("Nie znaleziono użytkownika: {}".format(user_id))
            if not user_id:
                user_info_doc[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
            yield self.insert(constants.COLLECTION_USERS_INFO, user_info_doc)
            user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(pipeline, USER_INFO_LIMIT_FIELDS)

            # if user has photo
            if constants.HAS_PHOTO in user_info_doc and user_info_doc[constants.HAS_PHOTO]:
                photo_doc = yield self.api_photo(user_info_doc[constants.ID])
                if photo_doc:
                    user_info_doc[constants.HAS_PHOTO] = settings.DEPLOY_API + '/users_info_photos/' + str(photo_doc[constants.MONGO_ID])
                    yield self.update(constants.COLLECTION_USERS_INFO, user_info_doc[constants.MONGO_ID], user_info_doc)

        raise gen.Return(user_info_doc)

    @gen.coroutine
    def api_faculty(self, faculty_id):
        pipeline = {constants.FACULTY_ID: faculty_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_FACULTIES, pipeline)

        faculty_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one(pipeline, LIMIT_FIELDS_FACULTY)

        if not faculty_doc:
            faculty_doc = yield self.usos_faculty(faculty_id)
            yield self.insert(constants.COLLECTION_FACULTIES, faculty_doc)

        raise gen.Return(faculty_doc)

    @gen.coroutine
    def api_group(self, course_id, term_id, group_id, finish=True):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: usos_doc[constants.USOS_ID],
                    constants.TERM_ID: term_id, 'course_unit_id': group_id}

        if self.do_refresh():
            yield self.remove(constants.COLLECTION_GROUPS, pipeline)

        group_doc = yield self.db[constants.COLLECTION_GROUPS].find_one(pipeline, LIMIT_FIELDS_GROUPS)

        if not group_doc:
            try:
                group_doc = yield self.usos_group(group_id)
                yield self.insert(constants.COLLECTION_GROUPS, group_doc)
            except UsosClientError, ex:
                yield self.exc(ex, finish=finish)

        raise gen.Return(group_doc)

    @gen.coroutine
    def api_photo(self, user_info_id):
        pipeline = {constants.ID: user_info_id}
        if self.do_refresh():
            yield self.remove(constants.COLLECTION_PHOTOS, pipeline)

        photo_doc = yield self.db[constants.COLLECTION_PHOTOS].find_one(pipeline)

        if not photo_doc:
            photo_doc = yield self.usos_photo(user_info_id)
            photo_id = yield self.insert(constants.COLLECTION_PHOTOS, photo_doc)
            photo_doc = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.MONGO_ID: ObjectId(photo_id)})

        raise gen.Return(photo_doc)
