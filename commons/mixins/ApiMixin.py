# coding=UTF-8

import logging
from datetime import date, timedelta, datetime

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
LIMIT_FIELDS_COURSE_EDITION = ('lecturers', 'coordinators', 'participants', 'course_units_ids', 'grades')
LIMIT_FIELDS_GROUPS = ('class_type', 'group_number', 'course_unit_id')
LIMIT_FIELDS_FACULTY = (constants.FACULTY_ID, 'logo_urls', 'name', 'postal_address', 'homepage_url', 'phone_numbers',
                        'path', 'stats')
LIMIT_FIELDS_TERMS = ('name', 'start_date', 'end_date', 'finish_date')
LIMIT_FIELDS_USER = (
    'first_name', 'last_name', 'titles', 'email_url', constants.ID, constants.PHOTO_URL, 'staff_status', 'room',
    'office_hours', 'employment_positions', 'course_editions_conducted', 'interests', 'homepage_url')
LIMIT_FIELDS_PROGRAMMES = (
    'name', 'mode_of_studies', 'level_of_studies', 'programme_id', 'duration', 'description', 'faculty')
TERM_LIMIT_FIELDS = ('name', 'end_date', 'finish_date', 'start_date', 'name', 'term_id', constants.TERMS_ORDER_KEY)
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

            courses_editions_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

            await self.db_insert(constants.COLLECTION_COURSES_EDITIONS, courses_editions_doc)

        return courses_editions_doc

    async def usos_course_edition(self, course_id, term_id, fetch_participants):
        if fetch_participants:
            args = {
                'fields': 'course_name|grades|participants|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            }
        else:
            args = {
                'fields': 'course_name|coordinators|course_units_ids|lecturers',
                'course_id': course_id,
                'term_id': term_id
            }

        result = await UsosCaller(self._context).call(path='services/courses/course_edition', arguments=args)

        result[constants.COURSE_NAME] = result[constants.COURSE_NAME]['pl']
        result[constants.COURSE_ID] = course_id
        result[constants.TERM_ID] = term_id
        result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

        return result

    async def api_course_edition(self, course_id, term_id):

        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy kursów.")

        result = None
        for term, courses in list(courses_editions[constants.COURSE_EDITIONS].items()):
            if term != term_id:
                continue

            for course in courses:
                if course[constants.COURSE_ID] == course_id:
                    result = course
                    break

        if not result:
            try:
                result = await self.usos_course_edition(course_id, term_id, False)

                logging.debug('found extra course_edition for : {0} {1} not saving i'.format(course_id, term_id))
            except Exception as ex:
                await self.exc(ex, finish=False)

        return result

    async def api_course_term(self, course_id, term_id, user_id=None, extra_fetch=True):

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = await self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            try:
                course_doc = await self.usos_course(course_id)
                await self.db_insert(constants.COLLECTION_COURSES, course_doc)
            except DuplicateKeyError as ex:
                logging.warning(ex)
                course_doc = await self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)
            except Exception as ex:
                await self.exc(ex, finish=False)
                return

        course_doc[constants.TERM_ID] = term_id

        course_edition = await self.api_course_edition(course_id, term_id)

        if not course_edition:
            return

        if not user_id:
            user_info_doc = await self.api_user_info()
        else:
            user_info_doc = await self.api_user_info(user_id)

        if not user_info_doc:
            raise ApiError(
                "Błąd podczas pobierania danych użytkownika course_id {0} term_id {1}".format(course_id, term_id))

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
                    tasks_groups.append(self.api_group(int(unit)))

            groups = await gen.multi(tasks_groups)
            course_doc['groups'] = self.filterNone(groups)

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

        course_doc[constants.COURSE_NAME] = course_doc['name']['pl']
        course_doc.pop('name')
        course_doc['learning_outcomes'] = course_doc['learning_outcomes']['pl']
        course_doc['description'] = course_doc['description']['pl']
        course_doc['assessment_criteria'] = course_doc['assessment_criteria']['pl']
        course_doc['bibliography'] = course_doc['bibliography']['pl']
        course_doc['practical_placement'] = course_doc['practical_placement']['pl']
        course_doc[constants.COURSE_ID] = course_id

        return course_doc

    async def api_course(self, course_id):

        pipeline = {constants.COURSE_ID: course_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_COURSES, pipeline)

        course_doc = await self.db[constants.COLLECTION_COURSES].find_one(pipeline, LIMIT_FIELDS)

        if not course_doc:
            try:
                course_doc = await self.usos_course(course_id)

                await self.db_insert(constants.COLLECTION_COURSES, course_doc)
            except DuplicateKeyError as ex:
                logging.warning(ex)
            except Exception as ex:
                await self.exc(ex, finish=False)

            if not course_doc:
                return

            # change id to value
            course_doc['is_currently_conducted'] = usoshelper.dict_value_is_currently_conducted(
                course_doc['is_currently_conducted'])

            # change faculty_id to faculty name
            faculty_doc = await self.api_faculty(course_doc[constants.FACULTY_ID])
            if not faculty_doc:
                faculty_doc = await self.usos_faculty(course_doc[constants.FACULTY_ID])

            course_doc[constants.FACULTY_ID] = {constants.FACULTY_ID: faculty_doc[constants.FACULTY_ID],
                                                constants.FACULTY_NAME: faculty_doc[constants.FACULTY_NAME]}

            if not course_doc:
                raise ApiError("Nie znaleźliśmy danych kursu {0}".format(course_id))

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
                course[constants.COURSE_NAME] = course[constants.COURSE_NAME]['pl']
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

            await self.db_insert(constants.COLLECTION_COURSES_CLASSTYPES, classtypes)
        return classtypes

    @staticmethod
    def classtype_name(classtypes, key_id):
        for key, name in list(classtypes.items()):
            if str(key_id) == str(key):
                return name['name']['pl']
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

    async def api_lecturers(self):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy nauczycieli.")

        result = list()
        for term, courses in list(courses_editions[constants.COURSE_EDITIONS].items()):
            for course in courses:
                for lecturer in course[constants.LECTURERS]:
                    if lecturer not in result:
                        result.append(lecturer)
        result = sorted(result, key=lambda k: k['last_name'])
        return result

    async def api_lecturer(self, user_info_id):
        user_info = await self.api_user_info(user_info_id)
        return user_info

    async def api_programmes(self, finish=False):
        user_info = await self.api_user_info()

        programmes = []
        for program in user_info['student_programmes']:
            result = await self.api_programme(program['programme']['id'], finish=finish)
            if result:
                program['programme']['mode_of_studies'] = result['mode_of_studies']
                program['programme']['level_of_studies'] = result['level_of_studies']
                program['programme']['duration'] = result['duration']
                program['programme']['name'] = result['name']
                programmes.append(program)

        return programmes

    async def api_programme(self, programme_id, finish=True):
        pipeline = {constants.PROGRAMME_ID: programme_id}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_PROGRAMMES, pipeline)

        programme_doc = await self.db[constants.COLLECTION_PROGRAMMES].find_one(pipeline, LIMIT_FIELDS_PROGRAMMES)

        if not programme_doc:
            try:
                programme_doc = await AsyncCaller(self._context).call_async(
                    path='services/progs/programme',
                    arguments={
                        'fields': 'name|mode_of_studies|level_of_studies|duration|professional_status|faculty[id|name]',
                        'programme_id': programme_id,
                    }
                )

                programme_doc[constants.PROGRAMME_ID] = programme_id

                # strip english names
                programme_doc['name'] = programme_doc['name']['pl']
                programme_doc['mode_of_studies'] = programme_doc['mode_of_studies']['pl']
                programme_doc['level_of_studies'] = programme_doc['level_of_studies']['pl']
                programme_doc['professional_status'] = programme_doc['professional_status']['pl']
                programme_doc['duration'] = programme_doc['duration']['pl']
                if 'faculty' in programme_doc and 'name' in programme_doc['faculty']:
                    programme_doc['faculty']['name'] = programme_doc['faculty']['name']['pl']
                    programme_doc['faculty'][constants.FACULTY_ID] = programme_doc['faculty']['id']
                    del (programme_doc['faculty']['id'])

                await self.db_insert(constants.COLLECTION_PROGRAMMES, programme_doc)
            except DuplicateKeyError as ex:
                logging.warning(ex)
                programme_doc = await self.db[constants.COLLECTION_PROGRAMMES].find_one(
                    pipeline, LIMIT_FIELDS_PROGRAMMES)
            except Exception as ex:
                await self.exc(ex, finish=finish)
                return

        return programme_doc

    async def api_tt(self, given_date):

        try:
            if isinstance(given_date, str):
                given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))
            monday = given_date - timedelta(days=(given_date.weekday()) % 7)
        except Exception:
            raise ApiError("Data w niepoprawnym formacie.")

        user_id = self.getUserId()

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_TT, {constants.USER_ID: user_id})

        tt_doc = await self.db[constants.COLLECTION_TT].find_one({constants.USER_ID: user_id,
                                                                  constants.TT_STARTDATE: str(monday)})
        if not tt_doc:
            try:
                tt_response = await UsosCaller(self._context).call(
                    path='services/tt/user',
                    arguments={
                        'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
                        'start': given_date,
                        'days': '7'
                    })

                tt_doc = dict()
                tt_doc[constants.TT_STARTDATE] = str(given_date)
                tt_doc['tts'] = tt_response
                tt_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

                await self.db_insert(constants.COLLECTION_TT, tt_doc)
            except Exception as ex:
                await self.exc(ex, finish=False)
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
        tt_lecturers_fetch_task = list()
        for tt in tt_doc['tts']:
            tt_lecturers_fetch_task.append(self._api_tt_attach_lecturers(tt))
        tt_doc = await gen.multi(tt_lecturers_fetch_task)

        return self.filterNone(tt_doc)

    async def _api_tt_attach_lecturers(self, tt):
        lecturer_keys = ['id', 'first_name', 'last_name', 'titles']

        for lecturer in tt['lecturer_ids']:
            try:
                lecturer_info = await self.api_user_info(str(lecturer))
                if lecturer_info:
                    lecturer_info = dict([(key, lecturer_info[key]) for key in lecturer_keys])
                    tt['lecturers'] = list()
                    tt['lecturers'].append(lecturer_info)
                else:
                    await self.exc(ApiError("Błąd podczas pobierania nauczyciela {0} dla planu.".format(lecturer)),
                                   finish=False)
                    return
            except Exception as ex:
                await self.exc(ex, finish=False)

        if 'lecturer_ids' in tt:
            del (tt['lecturer_ids'])

        return tt

    async def _api_term_task(self, term_id):
        term_doc = None
        try:
            term_doc = await AsyncCaller(self._context).call_async(
                path='services/terms/term', arguments={'term_id': term_id}
            )
            term_doc['name'] = term_doc['name']['pl']
            term_doc[constants.TERM_ID] = term_doc.pop(constants.ID)

            await self.db_insert(constants.COLLECTION_TERMS, term_doc)
        except DuplicateKeyError as ex:
            logging.warning(ex)
        except Exception as ex:
            await self.exc(ex, finish=False)
        finally:
            return term_doc

    async def api_term(self, term_ids):

        pipeline = {constants.TERM_ID: {"$in": term_ids}, constants.USOS_ID: self.getUsosId()}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_TERMS, pipeline)

        cursor = self.db[constants.COLLECTION_TERMS].find(pipeline, TERM_LIMIT_FIELDS).sort("order_key", -1)
        terms_doc = await cursor.to_list(None)

        if not terms_doc:
            try:
                terms_task = list()
                for term_id in term_ids:
                    terms_task.append(self._api_term_task(term_id))
                await gen.multi(terms_task)
                cursor.rewind()
                terms_doc = await cursor.to_list(None)
            except Exception as ex:
                await self.exc(ex, finish=False)
                return

        today = date.today()
        for term in terms_doc:
            end_date = datetime.strptime(term['finish_date'], "%Y-%m-%d").date()
            if today <= end_date:
                term['active'] = True
            else:
                term['active'] = False
            del (term[constants.MONGO_ID])

        return terms_doc

    async def api_terms(self):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy jednostek.")

        terms_ids = list()
        for term_id in courses_editions[constants.COURSE_EDITIONS]:
            if term_id in terms_ids:
                continue
            terms_ids.append(term_id)

        result = await self.api_term(terms_ids)

        return result

    async def usos_faculty(self, faculty_id):
        faculty_doc = await AsyncCaller(self._context).call_async(
            path='services/fac/faculty',
            arguments={
                'fields': 'name|homepage_url|path[id|name]|phone_numbers|postal_address|stats[course_count|programme_count|staff_count]|static_map_urls|logo_urls[100x100]',
                'fac_id': faculty_id
            }
        )

        faculty_doc[constants.FACULTY_ID] = faculty_id
        faculty_doc['name'] = faculty_doc['name']['pl']
        if 'path' in faculty_doc:
            for elem in faculty_doc['path']:
                elem['name'] = elem['name']['pl']

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
                logging.warning(ex)
                faculty_doc = await self.db[constants.COLLECTION_FACULTIES].find_one(pipeline, LIMIT_FIELDS_FACULTY)
            except Exception as ex:
                await self.exc(ex, finish=False)

        return faculty_doc

    async def api_faculties(self):
        users_info_doc = await self.api_user_info()

        # get programmes for user
        programmes_ids = list()
        if 'student_programmes' in users_info_doc:
            for programme in users_info_doc['student_programmes']:
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
            if 'faculty' in programme_doc and programme_doc['faculty'][constants.FACULTY_ID] not in faculties_ids:
                faculties_ids.append(programme_doc['faculty'][constants.FACULTY_ID])

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

        pipeline = {constants.USER_ID: self.get_current_user()[constants.MONGO_ID]}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_THESES, pipeline)

        theses_doc = await self.db[constants.COLLECTION_THESES].find_one(pipeline)

        if not theses_doc:
            users_info_doc = await self.api_user_info()
            theses_doc = await UsosCaller(self._context).call(
                path='services/theses/user',
                arguments={
                    'user_id': users_info_doc[constants.ID],
                    'fields': 'authored_theses[id|type|title|authors|supervisors|faculty]',
                })

            if 'authored_theses' in theses_doc:
                for these in theses_doc['authored_theses']:
                    these['faculty']['name'] = these['faculty']['name']['pl']

            theses_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

            await self.db_insert(constants.COLLECTION_THESES, theses_doc)

        return theses_doc['authored_theses']
