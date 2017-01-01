# coding=UTF-8

import logging

from pymongo.errors import DuplicateKeyError
from tornado import gen

from commons import usoshelper
from commons.constants import fields, collections
from commons.errors import ApiError
from commons.mixins.ApiUserMixin import ApiUserMixin
from commons.mixins.MathMixin import MathMixin

LIMIT_FIELDS_COURSE = {'is_currently_conducted': 1, 'bibliography': 1, fields.COURSE_NAME: 1, fields.FACULTY_ID: 1,
                       'assessment_criteria': 1, fields.COURSE_ID: 1, 'homepage_url': 1, 'lang_id': 1,
                       'learning_outcomes': 1, 'description': 1, fields.MONGO_ID: 0}
LIMIT_FIELDS_GROUPS = {'class_type': 1, 'group_number': 1, 'course_unit_id': 1}
LIMIT_FIELDS_FACULTY = {fields.FACULTY_ID: 1, 'logo_urls': 1, 'name': 1, 'postal_address': 1, 'homepage_url': 1,
                        'phone_numbers': 1, 'path': 1, 'stats': 1, fields.MONGO_ID: 0}
LIMIT_FIELDS_PROGRAMMES = {'name': 1, 'mode_of_studies': 1, 'level_of_studies': 1, 'programme_id': 1, 'duration': 1,
                           'description': 1, 'faculty': 1, fields.MONGO_ID: 0}


class ApiMixin(ApiUserMixin, MathMixin):
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
        pipeline = {fields.USER_ID: self.getUserId()}

        if self.do_refresh():
            await self.db_remove(collections.COURSES_EDITIONS, pipeline)

        courses_editions_doc = await self.db[collections.COURSES_EDITIONS].find_one(
            pipeline, (fields.COURSE_EDITIONS,))

        if not courses_editions_doc:
            courses_editions_doc = await self.usosCall(
                path='services/courses/user',
                arguments={
                    'fields': 'course_editions[course_id|course_name|term_id|course_units_ids|grades|lecturers|participants|coordinators]',
                    'active_terms_only': 'false',
                })

            courses_editions_doc[fields.USER_ID] = self.getUserId()

            try:
                await self.db_insert(collections.COURSES_EDITIONS, courses_editions_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)
                courses_editions_doc = await self.db[collections.COURSES_EDITIONS].find_one(
                    pipeline, (fields.COURSE_EDITIONS,))

        return courses_editions_doc

    async def usos_course_edition(self, course_id, term_id, fetch_participants):
        if fetch_participants:
            result = await self.usosCall(path='services/courses/course_edition', arguments={
                'fields': 'course_name|grades|participants|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            })
        else:
            result = await self.asyncCall(path='services/courses/course_edition', arguments={
                'fields': 'course_name|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            })

        result[fields.COURSE_NAME] = result.pop(fields.COURSE_NAME)
        result[fields.COURSE_ID] = course_id
        result[fields.TERM_ID] = term_id
        result[fields.USER_ID] = self.getUserId()

        return result

    async def api_course_edition(self, course_id, term_id, courses_editions=None):

        if not courses_editions:
            courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy kursów.")

        for term, courses in list(courses_editions[fields.COURSE_EDITIONS].items()):
            if term != term_id:
                continue

            for course in courses:
                if course[fields.COURSE_ID] == course_id:
                    return course

        try:
            result = await self.usos_course_edition(course_id, term_id, False)
            result[fields.USOS_ID] = self.getUsosId()
            logging.warning('found extra course_edition for : {0} {1} not saving'.format(course_id, term_id))
            return result
        # except DuplicateKeyError as ex:
        #    logging.warning(ex)
        except Exception as ex:
            await self.exc(ex, finish=False)
            return

    async def api_course_term(self, course_id, term_id, extra_fetch=True, log_exception=True, courses_editions=False):

        pipeline = {fields.COURSE_ID: course_id, fields.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(collections.COURSES, pipeline)

        course_doc = await self.db[collections.COURSES].find_one(pipeline, LIMIT_FIELDS_COURSE)

        if not course_doc:
            try:
                course_doc = await self.usos_course(course_id)
                await self.db_insert(collections.COURSES, course_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)
                course_doc = await self.db[collections.COURSES].find_one(pipeline, LIMIT_FIELDS_COURSE)
            except Exception as ex:
                if log_exception:
                    await self.exc(ex, finish=False)
                return

        course_doc[fields.TERM_ID] = term_id

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
                    if participant[fields.USER_ID] == self._context.user_doc[fields.USOS_USER_ID]:
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
            faculty_doc = await self.api_faculty(course_doc[fields.FACULTY_ID])
            course_doc[fields.FACULTY_ID] = {fields.FACULTY_ID: faculty_doc[fields.FACULTY_ID],
                                             fields.FACULTY_NAME: faculty_doc[fields.FACULTY_NAME]}

        return course_doc

    async def usos_course(self, course_id):
        course_doc = await self.usosCall(
            path='services/courses/course',
            arguments={
                'course_id': course_id,
                'fields': 'name|homepage_url|profile_url|is_currently_conducted|fac_id|lang_id|description|bibliography|learning_outcomes|assessment_criteria|practical_placement'
            })

        course_doc[fields.COURSE_NAME] = course_doc.pop('name')
        course_doc[fields.COURSE_ID] = course_id

        return course_doc

    async def api_course(self, course_id):

        pipeline = {fields.COURSE_ID: course_id, fields.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(collections.COURSES, pipeline)

        course_doc = await self.db[collections.COURSES].find_one(pipeline, LIMIT_FIELDS_COURSE)

        if not course_doc:
            course_doc = await self.usos_course(course_id)
            try:
                await self.db_insert(collections.COURSES, course_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)

        self.__translate_currently_conducted(course_doc)

        # change faculty_id to faculty name
        faculty_doc = await self.api_faculty(course_doc[fields.FACULTY_ID])
        if not faculty_doc:
            faculty_doc = await self.usos_faculty(course_doc[fields.FACULTY_ID])

        course_doc[fields.FACULTY_ID] = {fields.FACULTY_ID: faculty_doc[fields.FACULTY_ID],
                                         fields.FACULTY_NAME: faculty_doc[fields.FACULTY_NAME]}

        return course_doc

    async def api_courses(self, course_fields=None):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy przedmiotów")

        # get terms
        terms = list()
        for term in courses_editions[fields.COURSE_EDITIONS]:
            term_with_courses = {
                'term': term,
                'term_data': courses_editions[fields.COURSE_EDITIONS][term]
            }
            terms.append(term_with_courses)

        # add groups to courses
        courses = list()
        for term in terms:
            for course in term['term_data']:
                cursor = self.db[collections.GROUPS].find(
                    {fields.COURSE_ID: course[fields.COURSE_ID],
                     fields.TERM_ID: course[fields.TERM_ID],
                     fields.USOS_ID: self.getUsosId()},
                    LIMIT_FIELDS_GROUPS
                )
                groups_doc = await cursor.to_list(None)
                course['groups'] = groups_doc
                del course['course_units_ids']
                courses.append(course)

        # limit to fields
        if course_fields:
            selected_courses = list()
            for course in courses:
                filtered_course = {k: course[k] for k in set(course_fields) & set(course.keys())}
                selected_courses.append(filtered_course)
        else:
            selected_courses = courses

        return selected_courses

    async def api_courses_by_term(self, course_fields=None):

        courses_edition = await self.api_courses(course_fields)

        # grouping grades by term
        courses = dict()
        terms = list()
        for course in courses_edition:
            if course[fields.TERM_ID] not in courses:
                courses[course[fields.TERM_ID]] = list()
                terms.append(course[fields.TERM_ID])
            courses[course[fields.TERM_ID]].append(course)

        # get course in order by terms order_keys
        terms_by_order = await self.api_term(terms)
        courses_sorted_by_term = list()
        for term in terms_by_order:
            courses_sorted_by_term.append({term[fields.TERM_ID]: courses[term[fields.TERM_ID]]})

        return courses_sorted_by_term

    async def get_classtypes(self):
        classtypes = await self.db[collections.COURSES_CLASSTYPES].find_one(
            {fields.USOS_ID: self.getUsosId()},
            {fields.MONGO_ID: False, fields.CREATED_TIME: False})

        if not classtypes:
            classtypes = await self.asyncCall(path='services/courses/classtypes_index',
                                              lang=False)
            try:
                await self.db_insert(collections.COURSES_CLASSTYPES, classtypes)
            except DuplicateKeyError as ex:
                logging.debug(ex)

        return classtypes

    @staticmethod
    def classtype_name(classtypes, key_id):
        for key, name in list(classtypes.items()):
            if str(key_id) == str(key):
                if isinstance(name, dict) and 'name' in name:
                    return name['name']
                else:
                    return str(name)
        return key_id

    async def api_grades(self):

        classtypes = await self.get_classtypes()
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy ocen.")

        result = list()
        for term, courses in list(courses_editions[fields.COURSE_EDITIONS].items()):
            for course in courses:
                if len(course['grades']['course_grades']) > 0:
                    for grade_key, grade_value in list(course['grades']['course_grades'].items()):
                        grade = {
                            'exam_session_number': grade_value['exam_session_number'],
                            'exam_id': grade_value['exam_id'],
                            'value_description': grade_value['value_description'],
                            'value_symbol': grade_value['value_symbol'],
                            fields.CLASS_TYPE: fields.GRADE_FINAL,
                        }
                        course_with_grade = {
                            fields.TERM_ID: term,
                            fields.COURSE_ID: course[fields.COURSE_ID],
                            fields.COURSE_NAME: course[fields.COURSE_NAME],
                            'grades': list()
                        }
                        course_with_grade['grades'].append(grade)
                        result.append(course_with_grade)

                if len(course['grades']['course_units_grades']) > 0:
                    grade = {
                        fields.TERM_ID: term,
                        fields.COURSE_ID: course[fields.COURSE_ID],
                        fields.COURSE_NAME: course[fields.COURSE_NAME],
                        'grades': list()
                    }

                    for unit in course['grades']['course_units_grades']:
                        for unit2 in course['grades']['course_units_grades'][unit]:
                            elem = course['grades']['course_units_grades'][unit][unit2]
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
            unit[fields.CLASS_TYPE_ID] = self.classtype_name(classtypes, (unit[fields.CLASS_TYPE_ID]))

        for course in result:
            if 'grades' in course:
                for grade in course['grades']:
                    if 'unit' in grade:
                        unit = grade['unit']
                        grade[fields.CLASS_TYPE] = 'Brak danych'
                        for unit_doc in units_doc:
                            if int(unit) == unit_doc[fields.UNIT_ID]:
                                grade[fields.CLASS_TYPE] = unit_doc[fields.CLASS_TYPE_ID]
                                del (grade['unit'])

        return result

    async def api_grades_byterm(self):

        grades = await self.api_grades()

        terms = list()
        grades_by_term = dict()

        # grouping grades by term
        for grade in grades:
            if grade[fields.TERM_ID] not in grades_by_term:
                grades_by_term[grade[fields.TERM_ID]] = list()
                terms.append(grade[fields.TERM_ID])
            grades_by_term[grade[fields.TERM_ID]].append(grade)

        # order grades by terms in order_keys as dictionary and reverse sort
        terms_by_order = await self.api_term(terms)
        grades_sorted_by_term = list()
        for term in terms_by_order:
            grades_sorted_by_term.append({fields.TERM_ID: term[fields.TERM_ID],
                                          'avr_grades': self._math_average_grades(
                                              grades_by_term[term[fields.TERM_ID]]),
                                          'courses': grades_by_term[term[fields.TERM_ID]]})
        return grades_sorted_by_term

    async def api_average_grades(self):
        grades = await self.api_grades()
        return self._math_average_grades(grades)

    async def api_programmes(self, finish=False, user_info=None):
        if not user_info:
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
        pipeline = {fields.PROGRAMME_ID: programme_id}

        if self.do_refresh():
            await self.db_remove(collections.PROGRAMMES, pipeline)

        programme_doc = await self.db[collections.PROGRAMMES].find_one(pipeline, LIMIT_FIELDS_PROGRAMMES)
        if programme_doc:
            return programme_doc

        try:
            programme_doc = await self.asyncCall(
                path='services/progs/programme',
                arguments={
                    'fields': 'name|mode_of_studies|level_of_studies|duration|professional_status|faculty[id|name]',
                    'programme_id': programme_id,
                }
            )

            programme_doc[fields.PROGRAMME_ID] = programme_id

            try:
                ects_used_sum = await self.usosCall(
                    path='services/credits/used_sum',
                    arguments={
                        'programme_id': programme_id
                    })

                programme_doc['ects_used_sum'] = ects_used_sum
            except Exception as ex:
                logging.debug(ex)
                programme_doc['ects_used_sum'] = None

            await self.db_insert(collections.PROGRAMMES, programme_doc)
            return programme_doc
        except DuplicateKeyError as ex:
            logging.debug(ex)
            programme_doc = await self.db[collections.PROGRAMMES].find_one(
                pipeline, LIMIT_FIELDS_PROGRAMMES)
            return programme_doc
        except Exception as ex:
            await self.exc(ex, finish=finish)

    async def usos_faculty(self, faculty_id):
        faculty_doc = await self.asyncCall(
            path='services/fac/faculty',
            arguments={
                'fields': 'name|homepage_url|path[id|name]|phone_numbers|postal_address|stats[course_count|programme_count|staff_count]|static_map_urls|logo_urls[100x100]',
                'fac_id': faculty_id
            }
        )

        # obejście wystepowania null w polach stats i homepage_url

        if not faculty_doc['homepage_url']:
            faculty_doc['homepage_url'] = ""
        if not faculty_doc['stats']['course_count']:
            faculty_doc['stats']['course_count'] = 0
        if not faculty_doc['stats']['programme_count']:
            faculty_doc['stats']['programme_count'] = 0
        if not faculty_doc['stats']['staff_count']:
            faculty_doc['stats']['staff_count'] = 0

        faculty_doc[fields.FACULTY_ID] = faculty_id

        return faculty_doc

    async def api_faculty(self, faculty_id):
        pipeline = {fields.FACULTY_ID: faculty_id, fields.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(collections.FACULTIES, pipeline)

        faculty_doc = await self.db[collections.FACULTIES].find_one(pipeline, LIMIT_FIELDS_FACULTY)

        if not faculty_doc:
            try:
                faculty_doc = await self.usos_faculty(faculty_id)

                await self.db_insert(collections.FACULTIES, faculty_doc)
            except DuplicateKeyError as ex:
                logging.debug(ex)
                faculty_doc = await self.db[collections.FACULTIES].find_one(pipeline, LIMIT_FIELDS_FACULTY)
            except Exception as ex:
                await self.exc(ex, finish=False)

        return faculty_doc

    async def api_faculties(self, user_info=None):
        if not user_info:
            user_info = await self.api_user_usos_info()

        # get programmes for user
        programmes_ids = list()
        if 'student_programmes' in user_info:
            for programme in user_info['student_programmes']:
                programmes_ids.append(programme['programme'][fields.ID])

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
            if 'faculty' in programme_doc and fields.ID in programme_doc['faculty'] and \
                            programme_doc['faculty'][fields.ID] not in faculties_ids:
                faculties_ids.append(programme_doc['faculty'][fields.ID])

        faculties = list()
        tasks_faculties = list()
        for faculty_id in faculties_ids:
            tasks_faculties.append(self.api_faculty(faculty_id))
        tasks_faculties_result = await gen.multi(tasks_faculties)

        for faculty_doc in tasks_faculties_result:
            faculties.append(faculty_doc)

        return self.filterNone(faculties)

    async def api_unit(self, unit_id, finish=False):
        pipeline = {fields.UNIT_ID: int(unit_id), fields.USOS_ID: self.getUsosId()}
        if self.do_refresh():
            await self.db_remove(collections.COURSES_UNITS, pipeline)

        unit_doc = await self.db[collections.COURSES_UNITS].find_one(pipeline)

        if not unit_doc:
            try:
                unit_doc = await self.asyncCall(
                    path='services/courses/unit',
                    arguments={
                        'fields': 'id|course_id|term_id|groups|classtype_id',
                        'unit_id': unit_id,
                    })

                unit_doc[fields.UNIT_ID] = unit_doc.pop(fields.ID)
                unit_doc = await self.db_insert(collections.COURSES_UNITS, unit_doc)
            except Exception as ex:
                await self.exc(ex, finish=finish)
        return unit_doc

    async def api_units(self, units_id, finish=False):
        pipeline = {fields.UNIT_ID: {"$in": list(map(int, units_id))},
                    fields.USOS_ID: self.getUsosId()}
        cursor = self.db[collections.COURSES_UNITS].find(pipeline).sort("unit_id")
        units_doc = await cursor.to_list(None)

        # check what units are not in mongo
        missing_units = list()
        for unit_id in units_id:
            found = 0
            for unit_doc_id in units_doc:
                if str(unit_id) == str(unit_doc_id[fields.UNIT_ID]):
                    found = 1
            if found == 0:
                missing_units.append(str(unit_id))

        # fetch missing units
        if len(missing_units) > 0:
            try:
                tasks_units = list()
                for unit_id in missing_units:
                    tasks_units.append(self.api_unit(unit_id))
                await gen.multi(tasks_units)
                cursor.rewind()
                units_doc = await cursor.to_list(None)
            except Exception as ex:
                await self.exc(ex, finish=finish)

        return units_doc

    async def api_group(self, group_id, finish=False):
        pipeline = {fields.GROUP_ID: group_id, fields.USOS_ID: self.getUsosId()}
        if self.do_refresh():
            await self.db_remove(collections.GROUPS, pipeline)

        group_doc = await self.db[collections.GROUPS].find_one(pipeline)
        if not group_doc:
            try:
                group_doc = await self.asyncCall(
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

                await self.db_insert(collections.GROUPS, group_doc)
            except Exception as ex:
                await self.exc(ex, finish=finish)

        return group_doc

    async def api_thesis(self, refresh=False, user_info=None):

        pipeline = {fields.USER_ID: self.getUserId()}
        if self.do_refresh() and refresh:
            await self.db_remove(collections.THESES, pipeline)

        theses_doc = await self.db[collections.THESES].find_one(pipeline)

        if not theses_doc:
            if not user_info:
                user_info = await self.api_user_usos_info()

            theses_doc = await self.usosCall(
                path='services/theses/user',
                arguments={
                    'user_id': user_info[fields.ID],
                    'fields': 'authored_theses[id|type|title|authors|supervisors|faculty]',
                })

            theses_doc[fields.USER_ID] = self.getUserId()

            await self.db_insert(collections.THESES, theses_doc)

        return theses_doc['authored_theses']
