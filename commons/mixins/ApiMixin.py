# coding=UTF-8

import logging

from pymongo.errors import DuplicateKeyError
from tornado import gen

from commons import constants
from commons import usoshelper
from commons.UsosCaller import UsosCaller, AsyncCaller
from commons.errors import ApiError
from commons.mixins.ApiUserMixin import ApiUserMixin

LIMIT_FIELDS = (
    'is_currently_conducted', 'bibliography', constants.COURSE_NAME, constants.FACULTY_ID, 'assessment_criteria',
    constants.COURSE_ID, 'homepage_url', 'lang_id', 'learning_outcomes', 'description')
LIMIT_FIELDS_GROUPS = ('class_type', 'group_number', 'course_unit_id')
LIMIT_FIELDS_FACULTY = (constants.FACULTY_ID, 'logo_urls', 'name', 'postal_address', 'homepage_url', 'phone_numbers',
                        'path', 'stats')
LIMIT_FIELDS_USER = (
    'first_name', 'last_name', 'titles', 'email_url', constants.ID, constants.PHOTO_URL, 'staff_status', 'room',
    'office_hours', 'employment_positions', 'course_editions_conducted', 'interests', 'homepage_url')
LIMIT_FIELDS_PROGRAMMES = (
    'name', 'mode_of_studies', 'level_of_studies', 'programme_id', 'duration', 'description', 'faculty')
USER_INFO_LIMIT_FIELDS = (
    'first_name', 'last_name', constants.ID, 'student_number', 'student_status', constants.PHOTO_URL,
    'student_programmes',
    'user_type', constants.PHOTO_URL, 'has_photo', 'staff_status', 'employment_positions', 'room',
    'course_editions_conducted',
    'titles', 'office_hours', 'homepage_url', 'has_email', 'email_url', 'sex', 'user_id')


class ApiMixin(ApiUserMixin):
    @staticmethod
    def filterNone(array):
        return [i for i in array if i is not None]

    def __translate_currently_conducted(self, course_doc):
        # translate is_currently_conducted and course_is_currently_conducted number to string
        if 'is_currently_conducted' in course_doc:
            course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
                course_doc['is_currently_conducted'])
        if 'course_is_currently_conducted' in course_doc:
            course_doc['course_is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
                course_doc['course_is_currently_conducted'])

    async def api_courses_editions(self):
        pipeline = {constants.USER_ID: self.getUserId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_COURSES_EDITIONS, pipeline)

        courses_editions_doc = await self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            pipeline, (constants.COURSE_EDITIONS,))

        if not courses_editions_doc:
            courses_editions_doc = await UsosCaller(self._context).call(
                path='services/courses/user',
                arguments={
                    'fields': 'course_editions[course_id|course_name|term_id|course_units_ids|grades|lecturers|participants|coordinators]',
                    'active_terms_only': 'false',
                })

            courses_editions_doc[constants.USER_ID] = self.getUserId()

            try:
                await self.db_insert(constants.COLLECTION_COURSES_EDITIONS, courses_editions_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)
                courses_editions_doc = await self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
                    pipeline, (constants.COURSE_EDITIONS,))

        return courses_editions_doc

    async def usos_course_edition(self, course_id, term_id, fetch_participants):
        if fetch_participants:
            result = await UsosCaller(self._context).call(path='services/courses/course_edition', arguments={
                'fields': 'course_name|grades|participants|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            })
        else:
            result = await AsyncCaller(self._context).call_async(path='services/courses/course_edition', arguments={
                'fields': 'course_name|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            })

        result[constants.COURSE_NAME] = result.pop(constants.COURSE_NAME)
        result[constants.COURSE_ID] = course_id
        result[constants.TERM_ID] = term_id
        result[constants.USER_ID] = self.getUserId()

        return result

    async def api_course_edition(self, course_id, term_id, courses_editions=None):

        if not courses_editions:
            courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy kursów.")

        for term, courses in list(courses_editions[constants.COURSE_EDITIONS].items()):
            if term != term_id:
                continue

            for course in courses:
                if course[constants.COURSE_ID] == course_id:
                    return course

        try:
            result = await self.usos_course_edition(course_id, term_id, False)
            result[constants.USOS_ID] = self.getUsosId()
            logging.warning('found extra course_edition for : {0} {1} not saving'.format(course_id, term_id))
            return result
        # except DuplicateKeyError as ex:
        #    logging.warning(ex)
        except Exception as ex:
            await self.exc(ex, finish=False)
            return

    async def api_course_term(self, course_id, term_id, extra_fetch=True, log_exception=True, courses_editions=False):

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = await self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            try:
                course_doc = await self.usos_course(course_id)
                await self.db_insert(constants.COLLECTION_COURSES, course_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)
                course_doc = await self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)
            except Exception as ex:
                if log_exception:
                    await self.exc(ex, finish=False)
                return

        course_doc[constants.TERM_ID] = term_id

        course_edition = await self.api_course_edition(course_id, term_id, courses_editions)

        if not course_edition:
            return

        try:
            participants = list()
            if 'participants' in course_edition:
                # sort participants
                course_doc['participants'] = sorted(course_edition['participants'], key=lambda k: k['last_name'])

                participants = course_doc['participants']
                for participant in course_doc['participants']:
                    if participant[constants.USER_ID] == self._context.user_doc[constants.USOS_USER_ID]:
                        participants.remove(participant)
                        break

                course_doc['participants'] = participants
        except Exception as ex:
            logging.debug(ex)
            course_doc['participants'] = participants

        self.__translate_currently_conducted(course_doc)

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
                    tasks_groups.append(self.api_group(int(unit)))

            groups = await gen.multi(tasks_groups)
            groups_translated = []
            for group in self.filterNone(groups):
                groups_translated.append(self.__translate_currently_conducted(group))
            course_doc['groups'] = self.filterNone(groups_translated)

        if extra_fetch:
            term_doc = await self.api_term([term_id])
            course_doc['term'] = list()
            for term in term_doc:
                course_doc['term'].append(term)

        if extra_fetch:
            faculty_doc = await self.api_faculty(course_doc[constants.FACULTY_ID])
            course_doc[constants.FACULTY_ID] = {constants.FACULTY_ID: faculty_doc[constants.FACULTY_ID],
                                                constants.FACULTY_NAME: faculty_doc[constants.FACULTY_NAME]}

        course_doc.pop(constants.MONGO_ID)
        return course_doc

    async def usos_course(self, course_id):
        course_doc = await UsosCaller(self._context).call(
            path='services/courses/course',
            arguments={
                'course_id': course_id,
                'fields': 'name|homepage_url|profile_url|is_currently_conducted|fac_id|lang_id|description|bibliography|learning_outcomes|assessment_criteria|practical_placement'
            })

        course_doc[constants.COURSE_NAME] = course_doc.pop('name')
        course_doc[constants.COURSE_ID] = course_id

        return course_doc

    async def api_course(self, course_id):

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = await self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            course_doc = await self.usos_course(course_id)
            try:
                await self.db_insert(constants.COLLECTION_COURSES, course_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)

        self.__translate_currently_conducted(course_doc)

        # change faculty_id to faculty name
        faculty_doc = await self.api_faculty(course_doc[constants.FACULTY_ID])
        if not faculty_doc:
            faculty_doc = await self.usos_faculty(course_doc[constants.FACULTY_ID])

        course_doc[constants.FACULTY_ID] = {constants.FACULTY_ID: faculty_doc[constants.FACULTY_ID],
                                            constants.FACULTY_NAME: faculty_doc[constants.FACULTY_NAME]}

        return course_doc

    async def api_courses(self, fields=None):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy przedmiotów")

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
                     constants.USOS_ID: self.getUsosId()},
                    LIMIT_FIELDS_GROUPS
                )
                groups_doc = await cursor.to_list(None)
                course['groups'] = groups_doc
                del course['course_units_ids']
                courses.append(course)

        # limit to fields
        if fields:
            selected_courses = list()
            for course in courses:
                filtered_course = {k: course[k] for k in set(fields) & set(course.keys())}
                selected_courses.append(filtered_course)
        else:
            selected_courses = courses

        return selected_courses

    async def api_courses_by_term(self, fields=None):

        courses_edition = await self.api_courses(fields)

        # grouping grades by term
        courses = dict()
        terms = list()
        for course in courses_edition:
            if course[constants.TERM_ID] not in courses:
                courses[course[constants.TERM_ID]] = list()
                terms.append(course[constants.TERM_ID])
            courses[course[constants.TERM_ID]].append(course)

        # get course in order by terms order_keys
        terms_by_order = await self.api_term(terms)
        courses_sorted_by_term = list()
        for term in terms_by_order:
            courses_sorted_by_term.append({term[constants.TERM_ID]: courses[term[constants.TERM_ID]]})

        return courses_sorted_by_term

    async def get_classtypes(self):
        classtypes = await self.db[constants.COLLECTION_COURSES_CLASSTYPES].find_one(
            {constants.USOS_ID: self.getUsosId()},
            {constants.MONGO_ID: False, constants.CREATED_TIME: False})

        if not classtypes:
            classtypes = await AsyncCaller(self._context).call_async(path='services/courses/classtypes_index',
                                                                     lang=False)
            try:
                await self.db_insert(constants.COLLECTION_COURSES_CLASSTYPES, classtypes)
            except DuplicateKeyError as ex:
                logging.debug(ex)

        return classtypes

    @staticmethod
    def classtype_name(classtypes, key_id):
        for key, name in list(classtypes.items()):
            if str(key_id) == str(key):
                if 'pl' == name['name']:
                    return name['name']['pl']
                else:
                    return name['name']
        return key_id

    async def api_grades(self):

        classtypes = await self.get_classtypes()
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy ocen.")

        result = list()
        for term, courses in list(courses_editions[constants.COURSE_EDITIONS].items()):
            for course in courses:
                if len(course['grades']['course_grades']) > 0:
                    for grade_key, grade_value in list(course['grades']['course_grades'].items()):
                        grade = {
                            'exam_session_number': grade_value['exam_session_number'],
                            'exam_id': grade_value['exam_id'],
                            'value_description': grade_value['value_description'],
                            'value_symbol': grade_value['value_symbol'],
                            constants.CLASS_TYPE: constants.GRADE_FINAL,
                        }
                        course_with_grade = {
                            constants.TERM_ID: term,
                            constants.COURSE_ID: course[constants.COURSE_ID],
                            constants.COURSE_NAME: course[constants.COURSE_NAME],
                            'grades': list()
                        }
                        course_with_grade['grades'].append(grade)
                        result.append(course_with_grade)

                if len(course['grades']['course_units_grades']) > 0:
                    grade = {
                        constants.TERM_ID: term,
                        constants.COURSE_ID: course[constants.COURSE_ID],
                        constants.COURSE_NAME: course[constants.COURSE_NAME],
                        'grades': list()
                    }

                    for unit in course['grades']['course_units_grades']:
                        for unit2 in course['grades']['course_units_grades'][unit]:
                            elem = course['grades']['course_units_grades'][unit][unit2]
                            elem['value_description'] = elem['value_description']
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

        units_doc = await self.api_units(units)

        for unit in units_doc:
            unit[constants.CLASS_TYPE_ID] = self.classtype_name(classtypes, (unit[constants.CLASS_TYPE_ID]))

        for course in result:
            if 'grades' in course:
                for grade in course['grades']:
                    if 'unit' in grade:
                        unit = grade['unit']
                        for unit_doc in units_doc:
                            if int(unit) == unit_doc[constants.UNIT_ID]:
                                grade[constants.CLASS_TYPE] = unit_doc[constants.CLASS_TYPE_ID]
                                del (grade['unit'])
                            else:
                                grade[constants.CLASS_TYPE] = 'Brak danych'

        return result

    async def api_grades_byterm(self):

        grades = await self.api_grades()

        terms = list()
        grades_by_term = dict()

        # grouping grades by term
        for grade in grades:
            if grade[constants.TERM_ID] not in grades_by_term:
                grades_by_term[grade[constants.TERM_ID]] = list()
                terms.append(grade[constants.TERM_ID])
            grades_by_term[grade[constants.TERM_ID]].append(grade)

        # order grades by terms in order_keys as dictionary and reverse sort
        terms_by_order = await self.api_term(terms)
        grades_sorted_by_term = list()
        for term in terms_by_order:
            grades_sorted_by_term.append({constants.TERM_ID: term[constants.TERM_ID],
                                          'courses': grades_by_term[term[constants.TERM_ID]]})
        return grades_sorted_by_term

    async def api_programmes(self, finish=False):
        user_info = await self.api_user_usos_info()

        programmes = list()
        for program in user_info['student_programmes']:
            result = await self.api_programme(program['programme']['id'], finish=finish)
            if result:
                program['programme']['mode_of_studies'] = result['mode_of_studies']
                program['programme']['level_of_studies'] = result['level_of_studies']
                program['programme']['duration'] = result['duration']
                program['programme']['name'] = result['name']
                if 'ects_used_sum' in result:
                    program['programme']['ects_used_sum'] = result['ects_used_sum']
                else:
                    program['programme']['ects_used_sum'] = None
                programmes.append(program)

        return programmes

    async def api_programme(self, programme_id, finish=True):
        pipeline = {constants.PROGRAMME_ID: programme_id}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_PROGRAMMES, pipeline)

        programme_doc = await self.db[constants.COLLECTION_PROGRAMMES].find_one(pipeline, LIMIT_FIELDS_PROGRAMMES)
        if programme_doc:
            return programme_doc

        try:
            programme_doc = await AsyncCaller(self._context).call_async(
                path='services/progs/programme',
                arguments={
                    'fields': 'name|mode_of_studies|level_of_studies|duration|professional_status|faculty[id|name]',
                    'programme_id': programme_id,
                }
            )

            programme_doc[constants.PROGRAMME_ID] = programme_id

            try:
                ects_used_sum = await UsosCaller(self._context).call(
                    path='services/credits/used_sum',
                    arguments={
                        'programme_id': programme_id
                    })

                programme_doc['ects_used_sum'] = ects_used_sum
            except Exception as ex:
                await self.exc(ex, finish=False)
                programme_doc['ects_used_sum'] = None

            await self.db_insert(constants.COLLECTION_PROGRAMMES, programme_doc)
            return programme_doc
        except DuplicateKeyError as ex:
            logging.debug(ex)
            programme_doc = await self.db[constants.COLLECTION_PROGRAMMES].find_one(
                pipeline, LIMIT_FIELDS_PROGRAMMES)
            return programme_doc
        except Exception as ex:
            await self.exc(ex, finish=finish)

    async def usos_faculty(self, faculty_id):
        faculty_doc = await AsyncCaller(self._context).call_async(
            path='services/fac/faculty',
            arguments={
                'fields': 'name|homepage_url|path[id|name]|phone_numbers|postal_address|stats[course_count|programme_count|staff_count]|static_map_urls|logo_urls[100x100]',
                'fac_id': faculty_id
            }
        )

        faculty_doc[constants.FACULTY_ID] = faculty_id

        return faculty_doc

    async def api_faculty(self, faculty_id):
        pipeline = {constants.FACULTY_ID: faculty_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_FACULTIES, pipeline)

        faculty_doc = await self.db[constants.COLLECTION_FACULTIES].find_one(pipeline, LIMIT_FIELDS_FACULTY)

        if not faculty_doc:
            try:
                faculty_doc = await self.usos_faculty(faculty_id)

                await self.db_insert(constants.COLLECTION_FACULTIES, faculty_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)
                faculty_doc = await self.db[constants.COLLECTION_FACULTIES].find_one(pipeline, LIMIT_FIELDS_FACULTY)
            except Exception as ex:
                await self.exc(ex, finish=False)

        return faculty_doc

    async def api_faculties(self):
        user_info = await self.api_user_usos_info()

        # get programmes for user
        programmes_ids = list()
        if 'student_programmes' in user_info:
            for programme in user_info['student_programmes']:
                programmes_ids.append(programme['programme']['id'])

        programmes = []
        tasks_progammes = list()
        for programme_id in programmes_ids:
            tasks_progammes.append(self.api_programme(programme_id, finish=False))
        task_progammes_result = await gen.multi(tasks_progammes)

        for programme_doc in task_progammes_result:
            programmes.append(programme_doc)
        programmes = self.filterNone(programmes)

        # get faculties
        faculties_ids = list()
        for programme_doc in programmes:
            if 'faculty' in programme_doc and programme_doc['faculty'][constants.ID] not in faculties_ids:
                faculties_ids.append(programme_doc['faculty'][constants.ID])

        faculties = list()
        tasks_faculties = list()
        for faculty_id in faculties_ids:
            tasks_faculties.append(self.api_faculty(faculty_id))
        tasks_faculties_result = await gen.multi(tasks_faculties)

        for faculty_doc in tasks_faculties_result:
            faculties.append(faculty_doc)

        return self.filterNone(faculties)

    async def api_unit(self, unit_id, finish=False):
        pipeline = {constants.UNIT_ID: int(unit_id), constants.USOS_ID: self.getUsosId()}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_COURSES_UNITS, pipeline)

        unit_doc = await self.db[constants.COLLECTION_COURSES_UNITS].find_one(pipeline)

        if not unit_doc:
            try:
                unit_doc = await AsyncCaller(self._context).call_async(
                    path='services/courses/unit',
                    arguments={
                        'fields': 'id|course_id|term_id|groups|classtype_id',
                        'unit_id': unit_id,
                    })

                unit_doc[constants.UNIT_ID] = unit_doc.pop(constants.ID)
                unit_doc = await self.db_insert(constants.COLLECTION_COURSES_UNITS, unit_doc)
            except Exception as ex:
                await self.exc(ex, finish=finish)
        return unit_doc

    async def api_units(self, units_id, finish=False):
        pipeline = {constants.UNIT_ID: {"$in": list(map(int, units_id))},
                    constants.USOS_ID: self.getUsosId()}
        cursor = self.db[constants.COLLECTION_COURSES_UNITS].find(pipeline).sort("unit_id")
        units_doc = await cursor.to_list(None)

        if not units_doc:
            try:
                tasks_units = list()
                for unit in units_id:
                    tasks_units.append(self.api_unit(unit))
                await gen.multi(tasks_units)
                cursor.rewind()
                units_doc = await cursor.to_list(None)
            except Exception as ex:
                await self.exc(ex, finish=finish)

        return units_doc

    async def api_group(self, group_id, finish=False):
        pipeline = {constants.GROUP_ID: group_id, constants.USOS_ID: self.getUsosId()}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_GROUPS, pipeline)

        group_doc = await self.db[constants.COLLECTION_GROUPS].find_one(pipeline)
        if not group_doc:
            try:
                group_doc = await AsyncCaller(self._context).call_async(
                    path='services/groups/group',
                    arguments={
                        'fields': 'course_unit_id|group_number|class_type_id|class_type|course_id|term_id|course_is_currently_conducted|course_assessment_criteria',
                        'course_unit_id': group_id,
                        'group_number': 1,
                    })

                classtypes = await self.get_classtypes()
                group_doc['class_type'] = self.classtype_name(classtypes, group_doc[
                    'class_type_id'])  # changing class_type_id to name
                group_doc.pop('class_type_id')

                await self.db_insert(constants.COLLECTION_GROUPS, group_doc)
            except Exception as ex:
                await self.exc(ex, finish=finish)

        return group_doc

    async def api_thesis(self):

        pipeline = {constants.USER_ID: self.getUserId()}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_THESES, pipeline)

        theses_doc = await self.db[constants.COLLECTION_THESES].find_one(pipeline)

        if not theses_doc:
            user_info = await self.api_user_usos_info()

            theses_doc = await UsosCaller(self._context).call(
                path='services/theses/user',
                arguments={
                    'user_id': user_info[constants.ID],
                    'fields': 'authored_theses[id|type|title|authors|supervisors|faculty]',
                })

            theses_doc[constants.USER_ID] = self.getUserId()

            await self.db_insert(constants.COLLECTION_THESES, theses_doc)

        return theses_doc['authored_theses']
