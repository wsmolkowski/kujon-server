# coding=UTF-8

import logging
from collections import OrderedDict
from datetime import date, timedelta, datetime

from bson.objectid import ObjectId
from tornado import gen

from commons import constants, settings
from commons.errors import ApiError, UsosClientError
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin
from commons.usosutils import usoshelper

LIMIT_FIELDS = (
    'is_currently_conducted', 'bibliography', constants.COURSE_NAME, constants.FACULTY_ID, 'assessment_criteria',
    constants.COURSE_ID, 'homepage_url', 'lang_id', 'learning_outcomes', 'description')
LIMIT_FIELDS_COURSE_EDITION = ('lecturers', 'coordinators', 'participants', 'course_units_ids', 'grades')
LIMIT_FIELDS_GROUPS = ('class_type_id', 'group_number', 'course_unit_id')
LIMIT_FIELDS_FACULTY = (constants.FACULTY_ID, 'logo_urls', 'name', 'postal_address', 'homepage_url', 'phone_numbers',
                        'path', 'stats')
LIMIT_FIELDS_TERMS = ('name', 'start_date', 'end_date', 'finish_date')
LIMIT_FIELDS_USER = (
    'first_name', 'last_name', 'titles', 'email_url', constants.ID, constants.PHOTO_URL, 'staff_status', 'room',
    'office_hours', 'employment_positions', 'course_editions_conducted', 'interests', 'homepage_url')
LIMIT_FIELDS_PROGRAMMES = (
    'name', 'mode_of_studies', 'level_of_studies', 'programme_id', 'duration', 'description', 'faculty')
TERM_LIMIT_FIELDS = ('name', 'end_date', 'finish_date', 'start_date', 'name', 'term_id')
USER_INFO_LIMIT_FIELDS = (
    'first_name', 'last_name', constants.ID, 'student_number', 'student_status', constants.PHOTO_URL,
    'student_programmes',
    'user_type', constants.PHOTO_URL, 'has_photo', 'staff_status', 'employment_positions', 'room',
    'course_editions_conducted',
    'titles', 'office_hours', 'homepage_url', 'has_email', 'email_url', 'sex', 'user_id')


class ApiMixin(DaoMixin, UsosMixin):
    def do_refresh(self):
        return False

    @gen.coroutine
    def api_courses_editions(self):
        user_id = ObjectId(self.user_doc[constants.MONGO_ID])

        pipeline = {constants.USER_ID: user_id}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_COURSES_EDITIONS, pipeline)

        courses_editions_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            pipeline, (constants.COURSE_EDITIONS,))

        if not courses_editions_doc:
            courses_editions_doc = yield self.usos_courses_editions()
            yield self.db_insert(constants.COLLECTION_COURSES_EDITIONS, courses_editions_doc)

        raise gen.Return(courses_editions_doc)

    @gen.coroutine
    def api_course_edition(self, course_id, term_id):

        courses_editions = yield self.api_courses_editions()
        result = None
        for term, courses in courses_editions[constants.COURSE_EDITIONS].items():
            if term != term_id:
                continue

            for course in courses:
                if course[constants.COURSE_ID] == course_id:
                    result = course
                    break

        if not result:
            try:
                result = yield self.usos_course_edition(course_id, term_id, False)
                logging.debug('found extra course_edition for : {0} {1} not saving i'.format(course_id, term_id))
            except UsosClientError as ex:
                raise self.exc(ex, finish=False)

        raise gen.Return(result)

    @gen.coroutine
    def api_course_term(self, course_id, term_id, user_id=None, extra_fetch=True):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: usos_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            try:
                course_doc = yield self.usos_course(course_id)
                yield self.db_insert(constants.COLLECTION_COURSES, course_doc)
            except Exception, ex:
                logging.exception(ex)
                raise ApiError("Nie znaleźliśmy kursu", course_id)

        course_doc[constants.TERM_ID] = term_id

        course_edition = yield self.api_course_edition(course_id, term_id)

        if not course_edition:
            raise ApiError("Nie znaleźliśmy edycji kursu", (course_id, term_id))

        if not user_id:
            user_info_doc = yield self.api_user_info()
        else:
            user_info_doc = yield self.api_user_info(user_id)

        if not user_info_doc:
            raise ApiError("Błąd podczas pobierania danych użytkownika", (course_id, term_id))

        # checking if user is on this course, so have access to this course # FIXME
        if 'participants' in course_edition and constants.ID in user_info_doc:
            # sort participants
            course_doc['participants'] = sorted(course_edition['participants'], key=lambda k: k['last_name'])

            participants = course_doc['participants']
            for participant in course_doc['participants']:
                if participant[constants.USER_ID] == user_info_doc[constants.ID]:
                    participants.remove(participant)
                    break

            course_doc['participants'] = participants

        # change int to value
        course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
            course_doc['is_currently_conducted'])

        # make lecturers unique list
        course_doc['lecturers'] = list({item["id"]: item for item in course_edition['lecturers']}.values())
        course_doc['coordinators'] = course_edition['coordinators']
        course_doc['course_units_ids'] = course_edition['course_units_ids']
        if 'grades' in course_edition:
            course_doc['grades'] = course_edition['grades']
        else:
            course_doc['grades'] = None

        if extra_fetch:
            tasks_groups = list()
            if course_doc['course_units_ids']:
                for unit in course_doc['course_units_ids']:
                    tasks_groups.append(self.api_group(int(unit), finish=False))

            groups = yield tasks_groups
            course_doc['groups'] = filter(None, groups)  # remove None -> when USOS exception

        if extra_fetch:
            term_doc = yield self.api_term(term_id)
            if term_doc:
                course_doc['term'] = term_doc

        if extra_fetch:
            faculty_doc = yield self.api_faculty(course_doc[constants.FACULTY_ID])
            course_doc[constants.FACULTY_ID] = {constants.FACULTY_ID: faculty_doc[constants.FACULTY_ID],
                                                constants.FACULTY_NAME: faculty_doc[constants.FACULTY_NAME]}

        raise gen.Return(course_doc)

    @gen.coroutine
    def api_course(self, course_id):

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            try:
                course_doc = yield self.usos_course(course_id)
            except UsosClientError, ex:
                yield self.exc(ex, finish=True)
                raise gen.Return(None)

            yield self.db_insert(constants.COLLECTION_COURSES, course_doc)

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
        courses_editions = yield self.api_courses_editions()

        if not courses_editions:
            raise ApiError("Poczekaj szukamy przedmiotów")

        classtypes = yield self.db_classtypes()

        def classtype_name(key_id):
            for key, name in classtypes.items():
                if str(key_id) == str(key):
                    return name
            return key_id

        # get terms
        terms = list()
        for term in courses_editions[constants.COURSE_EDITIONS]:
            term_with_courses = {
                'term': term,
                'term_data': courses_editions[constants.COURSE_EDITIONS][term]
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
        terms_by_order = yield self.db_terms_with_order_keys(terms)
        terms_by_order = OrderedDict(sorted(terms_by_order.items(), reverse=True))
        courses_sorted_by_term = list()
        for order_key in terms_by_order:
            courses_sorted_by_term.append({terms_by_order[order_key]: courses[terms_by_order[order_key]]})

        raise gen.Return(courses_sorted_by_term)

    @gen.coroutine
    def api_grades(self):
        classtypes = yield self.db_classtypes()

        courses_editions = yield self.api_courses_editions()

        result = list()
        for term, courses in courses_editions[constants.COURSE_EDITIONS].items():
            for course in courses:
                if len(course['grades']['course_grades']) > 0:
                    for grade_key, grade_value in course['grades']['course_grades'].items():
                        grade = {
                            'exam_session_number': grade_value['exam_session_number'],
                            'exam_id': grade_value['exam_id'],
                            'value_description': grade_value['value_description']['pl'],
                            'value_symbol': grade_value['value_symbol'],
                            constants.CLASS_TYPE: constants.GRADE_FINAL,
                        }
                        course_with_grade = {
                            constants.TERM_ID: term,
                            constants.COURSE_ID: course[constants.COURSE_ID],
                            constants.COURSE_NAME: course[constants.COURSE_NAME]['pl'],
                            'grades': list()
                        }
                        course_with_grade['grades'].append(grade)
                        result.append(course_with_grade)

                if len(course['grades']['course_units_grades']) > 0:
                    grade = {
                        constants.TERM_ID: term,
                        constants.COURSE_ID: course[constants.COURSE_ID],
                        constants.COURSE_NAME: course[constants.COURSE_NAME]['pl'],
                        'grades': list()
                    }

                    for unit in course['grades']['course_units_grades']:
                        for unit2 in course['grades']['course_units_grades'][unit]:
                            elem = course['grades']['course_units_grades'][unit][unit2]
                            elem['value_description'] = elem['value_description']['pl']
                            elem['unit'] = unit
                            grade['grades'].append(elem)

                    # jeżeli są jakieś oceny
                    if len(grade['grades']) > 0:
                        result.append(grade)

        # wczytanie wszystkich unitów z ocen i zamiana ID typu zajęc na typ zajęć
        units = list()
        for course in result:
            for grade in course['grades']:
                if 'unit' in grade:
                    if grade['unit'] not in units:
                        units.append(grade['unit'])
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        pipeline = {'unit_id': {"$in": map(int, units)}, constants.USOS_ID: usos_doc[constants.USOS_ID]}
        cursor = self.db[constants.COLLECTION_COURSES_UNITS].find(pipeline,
                                                                  (constants.UNIT_ID, constants.CLASS_TYPE_ID))
        units_doc = yield cursor.to_list(None)
        for unit in units_doc:
            unit[constants.CLASS_TYPE_ID] = classtypes[(unit[constants.CLASS_TYPE_ID])]

        for course in result:
            if 'grades' in course:
                for grade in course['grades']:
                    if 'unit' in grade:
                        unit = grade['unit']
                        for unit_doc in units_doc:
                            if int(unit) == unit_doc[constants.UNIT_ID]:
                                grade[constants.CLASS_TYPE] = unit_doc[constants.CLASS_TYPE_ID]
                                del (grade['unit'])

        raise gen.Return(result)

    @gen.coroutine
    def api_grades_byterm(self):
        result = list()

        def find_grades(term_id):
            for term_grades in result:
                for key, value in term_grades.items():
                    if key == constants.TERM_ID and value == term_id:
                        return term_grades
            return None

        grades = yield self.api_grades()

        for grade in grades:
            term_grades = find_grades(grade[constants.TERM_ID])
            if term_grades:
                term_grades['courses'].append(grade)
                result.append(term_grades)
            else:
                result.append({
                    constants.TERM_ID: grade[constants.TERM_ID],
                    'courses': [grade]
                })

        raise gen.Return(result)

    @gen.coroutine
    def api_lecturers(self):
        courses_editions = yield self.api_courses_editions()

        result = list()
        for term, courses in courses_editions[constants.COURSE_EDITIONS].items():
            for course in courses:
                for lecturer in course[constants.LECTURERS]:
                    if lecturer not in result:
                        result.append(lecturer)

        raise gen.Return(result)

    @gen.coroutine
    def api_lecturer(self, user_info_id):

        user_info = yield self.api_user_info(user_info_id)

        if not user_info:
            raise ApiError("Poczekaj szukamy informacji o nauczycielu.", user_info_id)

        raise gen.Return(user_info)

    @gen.coroutine
    def api_programmes(self, finish=False):

        user_info = yield self.api_user_info()

        if not user_info:
            raise ApiError("Brak danych o użytkowniku.")

        programmes = []
        for program in user_info['student_programmes']:
            result = yield self.api_programme(program['programme']['id'], finish=finish)
            if result:
                program['programme']['mode_of_studies'] = result['mode_of_studies']
                program['programme']['level_of_studies'] = result['level_of_studies']
                program['programme']['duration'] = result['duration']
                program['programme']['name'] = result['name']
                programmes.append(program)

        raise gen.Return(programmes)

    @gen.coroutine
    def api_programme(self, programme_id, finish=True):
        pipeline = {constants.PROGRAMME_ID: programme_id}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_PROGRAMMES, pipeline)

        programme_doc = yield self.db[constants.COLLECTION_PROGRAMMES].find_one(pipeline, LIMIT_FIELDS_PROGRAMMES)

        if not programme_doc:
            try:
                programme_doc = yield self.usos_programme(programme_id)
                yield self.db_insert(constants.COLLECTION_PROGRAMMES, programme_doc)
            except UsosClientError, ex:
                yield self.exc(ex, finish=finish)

        raise gen.Return(programme_doc)

    @gen.coroutine
    def api_tt(self, given_date):

        monday = None
        if isinstance(given_date, str) or isinstance(given_date, unicode):
            try:
                given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))
                monday = given_date - timedelta(days=(given_date.weekday()) % 7)
            except Exception, ex:
                self.error("Niepoprawny format daty: RRRR-MM-DD.")
                yield self.exc(ex)
        else:
            monday = given_date - timedelta(days=(given_date.weekday()) % 7)

        user_id = ObjectId(self.user_doc[constants.MONGO_ID])

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_TT, {constants.USER_ID: user_id})

        tt_doc = yield self.db[constants.COLLECTION_TT].find_one({constants.USER_ID: user_id,
                                                                  constants.TT_STARTDATE: str(monday)})
        if not tt_doc:
            try:
                tt_doc = yield self.time_table(monday)
                yield self.db_insert(constants.COLLECTION_TT, tt_doc)
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
            yield self.db_remove(constants.COLLECTION_TERMS, pipeline)

        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one(pipeline, TERM_LIMIT_FIELDS)

        if not term_doc:
            try:
                term_doc = yield self.usos_term(term_id)
                yield self.db_insert(constants.COLLECTION_TERMS, term_doc)
            except UsosClientError as ex:
                yield self.exc(ex, finish=False)
                raise gen.Return(None)

        today = date.today()
        end_date = datetime.strptime(term_doc['finish_date'], "%Y-%m-%d").date()
        if today <= end_date:
            term_doc['active'] = True
        else:
            term_doc['active'] = False

        raise gen.Return(term_doc)

    @gen.coroutine
    def api_terms(self):
        courses_editions = yield self.api_courses_editions()

        api_terms = list()
        for term_id in courses_editions[constants.COURSE_EDITIONS]:
            if term_id in api_terms:
                continue
            api_terms.append(self.api_term(term_id))

        result = yield api_terms

        raise gen.Return(result)

    @gen.coroutine
    def api_user_info(self, user_id=None):

        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        if not user_id:
            pipeline = {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID]),
                        constants.USOS_ID: usos_doc[constants.USOS_ID]}
        else:
            pipeline = {constants.ID: user_id, constants.USOS_ID: usos_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_USERS_INFO, pipeline)

        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(pipeline, USER_INFO_LIMIT_FIELDS)

        if not user_info_doc:
            try:
                user_info_doc = yield self.usos_user_info(user_id)
            except UsosClientError as ex:
                yield self.exc(ex, finish=False)

            if not user_info_doc:
                raise ApiError("Nie znaleziono użytkownika: {0}".format(user_id))
            if not user_id:
                user_info_doc[constants.USER_ID] = self.user_doc[constants.MONGO_ID]

            # if user has photo
            if 'has_photo' in user_info_doc and user_info_doc['has_photo']:
                photo_doc = yield self.api_photo(user_info_doc[constants.ID])
                if photo_doc:
                    user_info_doc[constants.PHOTO_URL] = settings.DEPLOY_API + '/users_info_photos/' + str(
                        photo_doc[constants.MONGO_ID])

            yield self.db_insert(constants.COLLECTION_USERS_INFO, user_info_doc)
            user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(pipeline, USER_INFO_LIMIT_FIELDS)

        raise gen.Return(user_info_doc)

    @gen.coroutine
    def api_faculty(self, faculty_id):
        pipeline = {constants.FACULTY_ID: faculty_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_FACULTIES, pipeline)

        faculty_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one(pipeline, LIMIT_FIELDS_FACULTY)

        if not faculty_doc:
            faculty_doc = yield self.usos_faculty(faculty_id)
            yield self.db_insert(constants.COLLECTION_FACULTIES, faculty_doc)

        raise gen.Return(faculty_doc)

    @gen.coroutine
    def api_faculties(self):
        users_info_doc = yield self.api_user_info()

        # get programmes for user
        programmes_ids = list()
        if 'student_programmes' in users_info_doc:
            for programme in users_info_doc['student_programmes']:
                programmes_ids.append(programme['programme']['id'])

        programmes = []
        tasks_progammes = list()
        for programme_id in programmes_ids:
            tasks_progammes.append(self.api_programme(programme_id, finish=False))
        task_progammes_result = yield tasks_progammes
        for programme_doc in task_progammes_result:
            programmes.append(programme_doc)
        programmes = filter(None, programmes)

        # get faculties
        faculties_ids = list()
        for programme_doc in programmes:
            if 'faculty' in programme_doc and programme_doc['faculty'][constants.FACULTY_ID] not in faculties_ids:
                faculties_ids.append(programme_doc['faculty'][constants.FACULTY_ID])

        faculties = []
        tasks_faculties = list()
        for faculty_id in faculties_ids:
            tasks_faculties.append(self.api_faculty(faculty_id))
        tasks_faculties_result = yield tasks_faculties
        for faculty_doc in tasks_faculties_result:
            faculties.append(faculty_doc)

        faculties = filter(None, faculties)
        raise gen.Return(faculties)

    @gen.coroutine
    def api_unit(self, unit_id, finish=False):
        pipeline = {constants.UNIT_ID: unit_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}
        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_COURSES_UNITS, pipeline)

        unit_doc = yield self.db[constants.COLLECTION_COURSES_UNITS].find_one(pipeline)

        if not unit_doc:
            try:
                result = yield self.usos_unit(unit_id)
                if result:
                    yield self.db_insert(constants.COLLECTION_COURSES_UNITS, result)
                else:
                    logging.warning("no unit for unit_id: {0} and usos_id: {1)".format(unit_id, self.usos_id))
            except UsosClientError, ex:
                yield self.exc(ex, finish=finish)
        raise gen.Return(None)

    @gen.coroutine
    def api_group(self, group_id, finish=False):
        pipeline = {constants.GROUP_ID: group_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}
        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_GROUPS, pipeline)

        group_doc = yield self.db[constants.COLLECTION_GROUPS].find_one(pipeline)
        if not group_doc:
            try:
                result = yield self.usos_group(group_id)
                if result:
                    yield self.db_insert(constants.COLLECTION_GROUPS, result)
                else:
                    msg = "no group for group_id: {} and usos_id: {}.".format(group_id, self.usos_id)
                    logging.info(msg)
            except UsosClientError, ex:
                yield self.exc(ex, finish=finish)
        raise gen.Return(None)

    @gen.coroutine
    def api_photo(self, user_info_id):
        pipeline = {constants.ID: user_info_id}
        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_PHOTOS, pipeline)

        photo_doc = yield self.db[constants.COLLECTION_PHOTOS].find_one(pipeline)

        if not photo_doc:
            photo_doc = yield self.usos_photo(user_info_id)
            photo_id = yield self.db_insert(constants.COLLECTION_PHOTOS, photo_doc)
            photo_doc = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.MONGO_ID: ObjectId(photo_id)})

        raise gen.Return(photo_doc)
