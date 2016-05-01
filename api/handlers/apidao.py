# coding=UTF-8

from datetime import date, timedelta
from bson.objectid import ObjectId
from tornado import gen
from commons import constants, helpers, settings
from commons.errors import ApiError
from commons.usosutils import usoshelper
from commons.usosutils.usosclient import UsosClient
from database import DatabaseHandler

LIMIT_FIELDS = ('is_currently_conducted', 'bibliography', 'name', constants.FACULTY_ID, 'assessment_criteria',
                constants.COURSE_ID, 'homepage_url', 'lang_id', 'learning_outcomes', 'description')
LIMIT_FIELDS_COURSE_EDITION = ('lecturers', 'coordinators', 'participants', 'course_units_ids', 'grades')
LIMIT_FIELDS_GROUPS = ('class_type_id', 'group_number', 'course_unit_id')
LIMIT_FIELDS_FACULTY = (constants.FACULTY_ID, 'logo_urls', 'name', 'postal_address', 'homepage_url', 'phone_numbers')
LIMIT_FIELDS_TERMS = ('name', 'start_date', 'end_date', 'finish_date')

LIMIT_FIELDS_USER = (
    'first_name', 'last_name', 'titles', 'email_url', 'id', 'has_photo', 'staff_status', 'room', 'office_hours',
    'employment_positions', 'course_editions_conducted', 'interests', 'homepage_url')
LIMIT_FIELDS_PROGRAMMES = ('name', 'mode_of_studies', 'level_of_studies', 'programme_id', 'duration', 'description')


class ApiDaoHandler(DatabaseHandler):
    @gen.coroutine
    def api_course_term(self, course_id, term_id):
        usos_id = self.user_doc[constants.USOS_ID]
        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one(
            {constants.COURSE_ID: course_id,
             constants.USOS_ID: usos_id}, LIMIT_FIELDS)

        if not course_doc:
            raise ApiError("Niestety nie znaleźliśmy kursu", (course_id, term_id))

        # get information about course_edition
        course_edition_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
            {constants.COURSE_ID: course_id, constants.USOS_ID: usos_id,
             constants.TERM_ID: term_id}, LIMIT_FIELDS_COURSE_EDITION)
        if not course_edition_doc:
            raise ApiError("Błąd podczas pobierania edycji kursu", (course_id, term_id))

        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: self.user_doc[constants.MONGO_ID]})
        if not user_info_doc:
            raise ApiError("Błąd podczas pobierania danych użytkownika", (course_id, term_id))

        # checking if user is on this course, so have access to this course
        if 'participants' in course_edition_doc:
            # sort participants
            course_doc['participants'] = sorted(course_edition_doc['participants'], key=lambda k: k['last_name'])

            # check if user can see this course_edition (is on participant list)
            if not helpers.search_key_value_onlist(course_doc['participants'], constants.USER_ID,
                                                   user_info_doc[constants.ID]):
                raise ApiError("Nie masz uprawnień do wyświetlenie tej edycji kursu.", (course_id, term_id))
            else:
                # remove from participant list current user
                course_doc['participants'] = [participant for participant in course_doc['participants'] if
                                              participant[constants.USER_ID] != user_info_doc[constants.ID]]
        else:
            pass

        # change int to value
        course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
            course_doc['is_currently_conducted'])

        # get courses_classtypes
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: usos_id})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        # change faculty_id to faculty name
        fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: course_doc[
            constants.FACULTY_ID], constants.USOS_ID: usos_id}, LIMIT_FIELDS_FACULTY)
        course_doc.pop(constants.FACULTY_ID)
        course_doc[constants.FACULTY_ID] = fac_doc
        if 'pl' in course_doc['fac_id']['name']:
            course_doc['fac_id']['name'] = course_doc['fac_id']['name']['pl']

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
                    {constants.COURSE_ID: course_id, constants.USOS_ID: usos_id,
                     constants.TERM_ID: term_id, 'course_unit_id': int(unit)}, LIMIT_FIELDS_GROUPS)
                if not group_doc:
                    continue
                else:
                    group_doc[constants.CLASS_TYPE] = classtypes[group_doc[constants.CLASS_TYPE_ID]]
                    del (group_doc[constants.CLASS_TYPE_ID])
                    groups.append(group_doc)
        course_doc['groups'] = groups

        # terms
        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one(
            {constants.USOS_ID: usos_id,
             constants.TERM_ID: term_id}, LIMIT_FIELDS_TERMS)
        if not term_doc:
            pass
        else:
            term_doc['name'] = term_doc['name']['pl']
            course_doc['term'] = term_doc

        raise gen.Return(course_doc)

    @gen.coroutine
    def api_course(self, course_id):
        course_doc = yield self.db[constants.COLLECTION_COURSES].find_one({constants.COURSE_ID: course_id,
                                                                           constants.USOS_ID: self.user_doc[
                                                                               constants.USOS_ID]}, LIMIT_FIELDS)

        if not course_doc:
            raise ApiError("Nie znaleźliśmy danych kursu.", (course_id,))

        # change id to value
        course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
            course_doc['is_currently_conducted'])

        # change faculty_id to faculty name
        fac_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: course_doc[
            constants.FACULTY_ID], constants.USOS_ID: self.user_doc[constants.USOS_ID]}, LIMIT_FIELDS_FACULTY)
        course_doc.pop(constants.FACULTY_ID)
        if constants.FACULTY_ID in fac_doc:
            course_doc[constants.FACULTY_ID] = fac_doc
            course_doc[constants.FACULTY_ID]['name'] = course_doc[constants.FACULTY_ID]['name']['pl']

        raise gen.Return(course_doc)

    @gen.coroutine
    def api_courses(self):
        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])},
            ('course_editions', constants.MONGO_ID)
        )

        if not course_doc:
            raise ApiError("Poczekaj szukamy przedmiotów", 'brak')

        # get courses_classtypes
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: self.user_doc[
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
                     constants.USOS_ID: self.user_doc[constants.USOS_ID]},
                    LIMIT_FIELDS_GROUPS
                )
                groups = list()
                while (yield cursor.fetch_next):
                    group = cursor.next_object()
                    group['class_type'] = classtypes[group.pop('class_type_id')]  # changing class_type_id to name
                    groups.append(group)
                course['groups'] = groups
                course['course_name'] = course['course_name']['pl']
                del course['course_units_ids']
                courses.append(course)

        raise gen.Return(courses)

    @gen.coroutine
    def api_courses_by_term(self):
        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])},
            ('course_editions', constants.MONGO_ID)
        )

        if not course_doc:
            raise ApiError("Poczekaj szukamy przedmiotów", ["brak"])

        # get courses_classtypes
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: self.user_doc[
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
        for term in course_doc['course_editions']:
            for course in course_doc['course_editions'][term]:
                cursor = self.db[constants.COLLECTION_GROUPS].find(
                    {constants.COURSE_ID: course[constants.COURSE_ID],
                     constants.TERM_ID: term,
                     constants.USOS_ID: self.user_doc[constants.USOS_ID]},
                    LIMIT_FIELDS_GROUPS
                )
                groups = list()
                while (yield cursor.fetch_next):
                    group = cursor.next_object()
                    group['class_type_id'] = classtypes[group.pop('class_type_id')]  # changing class_type_id to name
                    groups.append(group)
                course['groups'] = groups
                course[constants.COURSE_NAME] = course[constants.COURSE_NAME]['pl']
                del course['course_units_ids']
                del course[constants.TERM_ID]

        raise gen.Return(course_doc['course_editions'])

    @gen.coroutine
    def api_grades(self):
        # get class_types
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find(
            {constants.USOS_ID: self.user_doc[constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        cursor = self.db[constants.COLLECTION_GRADES].find(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])},
            ('grades', constants.TERM_ID, constants.COURSE_ID,
             constants.COURSE_NAME)).sort([(constants.TERM_ID, -1)])
        new_grades = []

        while (yield cursor.fetch_next):
            grades_courseedition = cursor.next_object()
            grades_courseedition.pop(constants.MONGO_ID)
            grades_courseedition[constants.COURSE_NAME] = grades_courseedition[constants.COURSE_NAME]['pl']

            # if there is no grades -> pass
            if len(grades_courseedition['grades']['course_grades']) == 0 and \
                            len(grades_courseedition['grades']['course_units_grades']) == 0:
                continue

            units = {}
            for unit in grades_courseedition['grades']['course_units_grades']:
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

            if len(units) > 0:  # oceny czeciowe
                grades_courseedition['grades']['course_units'] = units
                for egzam in grades_courseedition['grades']['course_units_grades']:
                    for termin in grades_courseedition['grades']['course_units_grades'][egzam]:
                        elem = grades_courseedition['grades']['course_units_grades'][egzam][termin]
                        if int(egzam) in units:
                            elem[constants.CLASS_TYPE] = units[int(egzam)][constants.CLASS_TYPE_ID]
                        else:
                            elem[constants.CLASS_TYPE] = None
                        elem[constants.VALUE_DESCRIPTION] = elem[constants.VALUE_DESCRIPTION]['pl']
                        elem[constants.COURSE_ID] = grades_courseedition[constants.COURSE_ID]
                        elem[constants.COURSE_NAME] = grades_courseedition[constants.COURSE_NAME]
                        elem[constants.TERM_ID] = grades_courseedition[constants.TERM_ID]
                        new_grades.append(elem)
            else:  # ocena koncowa bez czesciowych
                for egzam in grades_courseedition['grades']['course_grades']:
                    elem = grades_courseedition['grades']['course_grades'][egzam]
                    elem[constants.VALUE_DESCRIPTION] = elem[constants.VALUE_DESCRIPTION]['pl']
                    elem[constants.CLASS_TYPE] = constants.GRADE_FINAL
                    elem[constants.COURSE_ID] = grades_courseedition[constants.COURSE_ID]
                    elem[constants.COURSE_NAME] = grades_courseedition[constants.COURSE_NAME]
                    elem[constants.TERM_ID] = grades_courseedition[constants.TERM_ID]
                    new_grades.append(elem)

        raise gen.Return(new_grades)

    @gen.coroutine
    def api_grades_byterm(self):
        # get class_types
        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find(
            {constants.USOS_ID: self.user_doc[constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        cursor = self.db[constants.COLLECTION_GRADES].find(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])},
            ('grades', constants.TERM_ID, constants.COURSE_ID,
             constants.COURSE_NAME)).sort([(constants.TERM_ID, -1)])
        new_grades = []

        while (yield cursor.fetch_next):
            grades_courseedition = cursor.next_object()
            grades_courseedition.pop(constants.MONGO_ID)
            grades_courseedition[constants.COURSE_NAME] = grades_courseedition[constants.COURSE_NAME]['pl']

            # if there is no grades -> pass
            if len(grades_courseedition['grades']['course_grades']) == 0 and \
                            len(grades_courseedition['grades']['course_units_grades']) == 0:
                continue

            units = {}
            for unit in grades_courseedition['grades']['course_units_grades']:
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

            if len(units) > 0:  # oceny czeciowe
                grades_courseedition['grades']['course_units'] = units
                for egzam in grades_courseedition['grades']['course_units_grades']:
                    for termin in grades_courseedition['grades']['course_units_grades'][egzam]:
                        elem = grades_courseedition['grades']['course_units_grades'][egzam][termin]
                        if int(egzam) in units:
                            elem[constants.CLASS_TYPE] = units[int(egzam)][constants.CLASS_TYPE_ID]
                        else:
                            elem[constants.CLASS_TYPE] = None
                        elem[constants.VALUE_DESCRIPTION] = elem[constants.VALUE_DESCRIPTION]['pl']
                        elem[constants.COURSE_ID] = grades_courseedition[constants.COURSE_ID]
                        elem[constants.COURSE_NAME] = grades_courseedition[constants.COURSE_NAME]
                        elem[constants.TERM_ID] = grades_courseedition[constants.TERM_ID]
                        new_grades.append(elem)
            else:  # ocena koncowa bez czesciowych
                for egzam in grades_courseedition['grades']['course_grades']:
                    elem = grades_courseedition['grades']['course_grades'][egzam]
                    elem[constants.VALUE_DESCRIPTION] = elem[constants.VALUE_DESCRIPTION]['pl']
                    elem[constants.CLASS_TYPE] = constants.GRADE_FINAL
                    elem[constants.COURSE_ID] = grades_courseedition[constants.COURSE_ID]
                    elem[constants.COURSE_NAME] = grades_courseedition[constants.COURSE_NAME]
                    elem[constants.TERM_ID] = grades_courseedition[constants.TERM_ID]
                    new_grades.append(elem)

        # grouping grades by term
        terms = dict()
        for grade in new_grades:
            if grade[constants.TERM_ID] not in terms:
                terms[grade[constants.TERM_ID]] = list()
            terms[grade[constants.TERM_ID]].append(grade)

        raise gen.Return(terms)

    @gen.coroutine
    def api_grade(self, course_id, term_id):
        pipeline = {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID]), constants.COURSE_ID: course_id,
                    constants.TERM_ID: term_id, constants.USOS_ID: self.user_doc[constants.USOS_ID]}

        limit_fields = ('course_name', 'course_id', 'grades')

        classtypes = {}
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: self.user_doc[
            constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        grades = yield self.db[constants.COLLECTION_GRADES].find_one(pipeline, limit_fields)
        units = {}
        if grades and len(grades) > 0:
            for unit in grades['grades']['course_units_grades']:
                pipeline = [{'$match': {'unit_id': int(unit), constants.USOS_ID: self.user_doc[constants.USOS_ID]}}, {
                    '$lookup': {'from': 'courses_classtypes', 'localField': 'classtype_id', 'foreignField': 'id',
                                'as': 'courses_classtypes'}}]
                unit_coursor = self.db[constants.COLLECTION_COURSES_UNITS].aggregate(pipeline)
                u = yield unit_coursor.to_list(None)
                for elem in u:
                    unit_id = elem['unit_id']
                    elem.pop('unit_id')
                    elem[constants.CLASS_TYPE_ID] = classtypes[(elem[constants.CLASS_TYPE_ID])]
                    units[unit_id] = elem
            if len(units) > 0:
                grades['grades']['course_units'] = units
                del grades['grades']['course_grades']
            else:
                del grades['grades']['course_units_grades']

        raise gen.Return(grades)

    @gen.coroutine
    def api_lecturers(self):
        courses = {}
        lecturers_returned = {}

        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])})
        if course_doc:
            for term in course_doc['course_editions']:
                for course in course_doc['course_editions'][term]:
                    courses[course[constants.COURSE_ID]] = course

            for course in courses:
                course_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
                    {constants.COURSE_ID: course, constants.TERM_ID: courses[course][constants.TERM_ID],
                     constants.USOS_ID: self.user_doc[constants.USOS_ID]})

                if not course_doc:
                    continue

                for lecturer in course_doc[constants.LECTURERS]:
                    lecturer_id = lecturer[constants.USER_ID]
                    lecturers_returned[lecturer_id] = lecturer

            lecturers_returned = lecturers_returned.values()

        raise gen.Return(lecturers_returned)

    @gen.coroutine
    def api_lecturer(self, user_info_id):
        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: user_info_id},
                                                                            LIMIT_FIELDS_USER)
        if not user_info:
            raise ApiError("Poczekaj szukamy informacji o nauczycielu.", (user_info_id,))

        # change ObjectId to str for photo
        if user_info['has_photo']:
            user_info['has_photo'] = str(user_info['has_photo'])

        # change staff_status to dictionary
        user_info['staff_status'] = usoshelper.dict_value_staff_status(user_info['staff_status'])

        # strip employment_positions from english names
        for position in user_info['employment_positions']:
            position['position']['name'] = position['position']['name']['pl']
            position['faculty']['name'] = position['faculty']['name']['pl']

        # change course_editions_conducted to list of courses
        course_editions = []
        if user_info['course_editions_conducted']:
            for courseterm in user_info['course_editions_conducted']:
                course_id, term_id = courseterm['id'].split('|')
                course_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
                    {constants.COURSE_ID: course_id, constants.TERM_ID: term_id,
                     constants.USOS_ID: self.user_doc[constants.USOS_ID]})
                if course_doc:
                    course = dict()
                    course[constants.COURSE_NAME] = course_doc[constants.COURSE_NAME]['pl']
                    course[constants.COURSE_ID] = course_doc[constants.COURSE_ID]
                    course[constants.TERM_ID] = course_doc[constants.TERM_ID]
                    course_editions.append(course)
                else:
                    course_editions.append("Dont have data for course and term..")
            user_info['course_editions_conducted'] = course_editions

        # show url to photo
        if user_info['has_photo']:
            user_info['has_photo'] = settings.DEPLOY_API + '/users_info_photos/' + str(user_info['has_photo'])

        raise gen.Return(user_info)

    @gen.coroutine
    def api_programmes(self):
        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])})

        if not user_info:
            raise ApiError("Szukamy danych o Twoich kursach", "brak")

        programmes = []
        for program in user_info['student_programmes']:
            result = yield self.db[constants.COLLECTION_PROGRAMMES].find_one(
                {constants.PROGRAMME_ID: program['programme']['id']}, LIMIT_FIELDS_PROGRAMMES)
            if result:
                program['programme']['mode_of_studies'] = result['mode_of_studies']
                program['programme']['level_of_studies'] = result['level_of_studies']
                program['programme']['duration'] = result['duration']
                program['programme']['name'] = result['name']
                programmes.append(program)
            else:
                ApiError("Nie znaleziono programu dla", program['programme']['id'])

        raise gen.Return(programmes)

    @gen.coroutine
    def api_tt(self, given_date):
        try:
            given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))
            monday = given_date - timedelta(days=(given_date.weekday()) % 7)
        except Exception, ex:
            self.error("Niepoprawny format daty - RRRR-MM-DD)")
            return

        # get user data
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: ObjectId(self.user_doc[constants.MONGO_ID])})
        # get usosdata for
        usos = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        # fetch TT from mongo
        tt_doc = yield self.db[constants.COLLECTION_TT].find_one(
            {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID]),
             constants.TT_STARTDATE: str(monday)})
        if not tt_doc:
            # fetch TT from USOS
            client = UsosClient(base_url=usos[constants.USOS_URL],
                                consumer_key=usos[constants.CONSUMER_KEY],
                                consumer_secret=usos[constants.CONSUMER_SECRET],
                                access_token_key=user_doc[constants.ACCESS_TOKEN_KEY],
                                access_token_secret=user_doc[constants.ACCESS_TOKEN_SECRET])
            try:
                result = client.time_table(monday)

                # insert TT to mongo
                tt_doc = dict()
                tt_doc[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
                tt_doc[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
                tt_doc[constants.TT_STARTDATE] = str(monday)
                if not result:
                    result = list()
                tt_doc['tts'] = result
                yield self.db[constants.COLLECTION_TT].insert(tt_doc)
            except Exception:
                self.error("Błąd podczas pobierania TT z USOS for {0}.".format(given_date))
                return

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
        for tt in tt_doc['tts']:
            for lecturer in tt['lecturer_ids']:
                lecturer_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
                    {constants.ID: str(lecturer)}, ('id','first_name','last_name','titles'))
                if not lecturer_info:
                    self.error("Błąd podczas pobierania nauczyciela (%r) dla planu.".format(lecturer))
                else:
                    tt['lecturers'] = list()
                    tt['lecturers'].append(lecturer_info)
            del(tt['lecturer_ids'])
        raise gen.Return(tt_doc['tts'])
