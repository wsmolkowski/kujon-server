# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from staracommon import constants

LIMIT_FIELDS = (
'first_name', 'last_name', 'titles', 'email_url', 'id', 'has_photo', 'staff_status', 'room', 'office_hours',
'employment_positions', 'course_editions_conducted', 'interests', 'homepage_url')


class LecturersApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        courses = {}
        lecturers_returned = {}

        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.ID])})
        if course_doc:
            for term in course_doc['course_editions']:
                for course in course_doc['course_editions'][term]:
                    courses[course[constants.COURSE_ID]] = course

            for course in courses:
                course_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
                    {constants.COURSE_ID: course, constants.TERM_ID: courses[course][constants.TERM_ID],
                     constants.USOS_ID: parameters[constants.USOS_ID]})

                if not course_doc:
                    continue

                for lecturer in course_doc[constants.LECTURERS]:
                    lecturer_id = lecturer[constants.USER_ID]

                    lecturer.pop('id')
                    lecturers_returned[lecturer_id] = lecturer


            lecturers_returned = lecturers_returned.values()
            lecturers_returned = sorted(lecturers_returned, key=lambda k: k['last_name'])
        if not lecturers_returned:
            self.error("Poczekaj szukamy nauczycieli..")
        else:
            self.success(lecturers_returned)


class LecturerByIdApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        parameters = yield self.get_parameters()

        user_info = yield self.db.users_info.find_one({constants.USER_INFO_ID: user_info_id}, LIMIT_FIELDS)
        if not user_info:
            self.error("Poczekaj szukamy informacji o nauczycielu..")
        else:

            # change staff_status to dictionary
            if user_info['staff_status'] == 1:
                user_info['staff_status'] = 'Pracownik'
            if user_info['staff_status'] == 2:
                user_info['staff_status'] = 'Nauczyciel akademicki'
            if user_info['staff_status'] == 0:
                user_info['staff_status'] = 'Nieaktywny pracownik'


            # change course_editions_conducted to list of courses
            course_editions = []
            if user_info['course_editions_conducted']:
                for courseterm in user_info['course_editions_conducted']:
                    course_id, term_id = courseterm['id'].split('|')
                    course_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
                        {constants.COURSE_ID: course_id, constants.TERM_ID: term_id,
                         constants.USOS_ID: parameters[constants.USOS_ID]})
                    if course_doc:
                        course_editions.append(course_doc)
                    else:
                        course_editions.append("Dont have data for course and term..")
                user_info['course_editions_conducted'] = course_editions
            self.success(user_info)
