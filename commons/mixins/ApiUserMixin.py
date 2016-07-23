# coding=utf-8

import logging

from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from tornado import gen

from commons import constants, settings
from commons import usoshelper
from commons.UsosCaller import UsosCaller
from commons.mixins.DaoMixin import DaoMixin

USER_INFO_SKIP_FIELDS = {constants.MONGO_ID: False, 'email_access': False, 'interests': False,
                         'employment_functions': False, constants.CREATED_TIME: False, 'email': False}


class ApiUserMixin(DaoMixin):
    def do_refresh(self):
        return False

    @gen.coroutine
    def usos_user_info(self, user_id=None):
        fields = 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'

        if user_id:
            result = yield UsosCaller(self._context).call(path='services/users/user',
                                                          arguments={'fields': fields, 'user_id': user_id})
        else:
            result = yield UsosCaller(self._context).call(path='services/users/user', arguments={'fields': fields})

        # strip english values and if value is empty change to None
        if 'office_hours' in result and 'pl' in result['office_hours']:
            result['office_hours'] = result['office_hours']['pl']
            result['interests'] = result['interests']['pl']

        # strip empty values
        if 'homepage_url' in result and result['homepage_url'] == "":
            result['homepage_url'] = None

        if 'student_status' in result:
            result['student_status'] = usoshelper.dict_value_student_status(result['student_status'])

        # strip english names from programmes description
        if 'student_programmes' in result:
            for programme in result['student_programmes']:
                programme['programme']['description'] = programme['programme']['description']['pl']

        # change staff_status to dictionary
        result['staff_status'] = usoshelper.dict_value_staff_status(result['staff_status'])

        # strip employment_positions from english names
        for position in result['employment_positions']:
            position['position']['name'] = position['position']['name']['pl']
            position['faculty']['name'] = position['faculty']['name']['pl']

        # strip english from building name
        if 'room' in result and result['room'] and 'building_name' in result['room']:
            result['room']['building_name'] = result['room']['building_name']['pl']

        raise gen.Return(result)

    @gen.coroutine
    def api_user_info(self, user_id=None):

        if not user_id:
            pipeline = {constants.USER_ID: ObjectId(self.get_current_user()[constants.MONGO_ID]),
                        constants.USOS_ID: self.get_current_usos()[constants.USOS_ID]}
        else:
            pipeline = {constants.ID: user_id, constants.USOS_ID: self.get_current_usos()[constants.USOS_ID]}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_USERS_INFO, pipeline)

        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(pipeline, USER_INFO_SKIP_FIELDS)

        if not user_info_doc:
            try:
                user_info_doc = yield self.usos_user_info(user_id)
            except Exception as ex:
                yield self.exc(ex, finish=False)

            if not user_info_doc:
                logging.error("api_user_info - nie znaleziono użytkownika: {0}".format(user_id))
                raise gen.Return()
            if not user_id:
                user_info_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

            # process faculties
            tasks_get_faculties = list()
            for position in user_info_doc['employment_positions']:
                tasks_get_faculties.append(self.api_faculty(position['faculty']['id']))
            yield tasks_get_faculties

            # process course_editions_conducted
            courses_conducted = []
            tasks_courses = list()
            courses = list()
            for course_conducted in user_info_doc['course_editions_conducted']:
                course_id, term_id = course_conducted['id'].split('|')
                if course_id not in courses:
                    courses.append(course_id)
                    tasks_courses.append(self.api_course_term(course_id, term_id, extra_fetch=False))

            try:
                tasks_results = yield tasks_courses
                for course_doc in tasks_results:
                    courses_conducted.append({constants.COURSE_NAME: course_doc[constants.COURSE_NAME],
                                              constants.COURSE_ID: course_doc[constants.COURSE_ID],
                                              constants.TERM_ID: course_doc[constants.TERM_ID]})
            except Exception as ex:
                yield self.exc(ex, finish=False)

            user_info_doc['course_editions_conducted'] = courses_conducted

            # if user has photo
            if 'has_photo' in user_info_doc and user_info_doc['has_photo']:
                photo_doc = yield self.api_photo(user_info_doc[constants.ID])
                if photo_doc:
                    user_info_doc[constants.PHOTO_URL] = settings.DEPLOY_API + '/users_info_photos/' + str(
                        photo_doc[constants.MONGO_ID])

            try:
                yield self.db_insert(constants.COLLECTION_USERS_INFO, user_info_doc)
            except DuplicateKeyError as ex:
                logging.warning(ex)
            finally:
                user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one(pipeline, USER_INFO_SKIP_FIELDS)

        if constants.MONGO_ID in user_info_doc:
            del (user_info_doc[constants.MONGO_ID])

        raise gen.Return(user_info_doc)
