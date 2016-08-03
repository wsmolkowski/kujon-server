# coding=utf-8

import logging

from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from tornado import gen

from commons import constants
from commons import usoshelper
from commons.UsosCaller import UsosCaller
from commons.errors import CallerError
from commons.mixins.DaoMixin import DaoMixin

USER_INFO_SKIP_FIELDS = {'email_access': False, 'interests': False,
                         'employment_functions': False, constants.CREATED_TIME: False, 'email': False}


class ApiUserMixin(DaoMixin):
    async def api_photo(self, user_info_id):
        pipeline = {constants.ID: user_info_id}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_PHOTOS, pipeline)

        photo_doc = await self.db[constants.COLLECTION_PHOTOS].find_one(pipeline)

        if not photo_doc:
            try:
                photo_doc = await UsosCaller(self._context).call(
                    path='services/photos/photo',
                    arguments={
                        'user_id': user_info_id,
                    })

                photo_doc[constants.ID] = user_info_id

                photo_id = await self.db_insert(constants.COLLECTION_PHOTOS, photo_doc)
                photo_doc = await self.db[constants.COLLECTION_PHOTOS].find_one(
                    {constants.MONGO_ID: ObjectId(photo_id)})
            except Exception as ex:
                logging.exception(ex)
        return photo_doc

    async def usos_user_info(self, user_id=None):
        fields = 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'

        if user_id:
            result = await UsosCaller(self._context).call(path='services/users/user',
                                                          arguments={'fields': fields, 'user_id': user_id})
        else:
            result = await UsosCaller(self._context).call(path='services/users/user', arguments={'fields': fields})

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

        # strip employment_function from english names
        for position in result['employment_functions']:
            position['function'] = position['function']['pl']
            position['faculty']['name'] = position['faculty']['name']['pl']

        # strip english from building name
        if 'room' in result and result['room'] and 'building_name' in result['room']:
            result['room']['building_name'] = result['room']['building_name']['pl']

        return result

    async def api_user_usos_info(self):
        try:
            user_usos_id = await self.db_user_usos_id()
            if user_usos_id:
                user_info_doc = await self.api_user_info(user_usos_id)
                return user_info_doc

            user_info_doc = await self.api_user_info()
            user_doc = await self.db_find_user()
            user_doc[constants.USOS_INFO_ID] = user_info_doc[constants.MONGO_ID]
            await self.db_update_user(user_doc[constants.MONGO_ID], user_doc)

            return user_info_doc
        except Exception as ex:
            await self.exc(ex, finish=False)
            return

    async def api_user_info(self, user_id=None):

        if not user_id:
            pipeline = {constants.USER_ID: self.getUserId(),
                        constants.USOS_ID: self.getUsosId()}
        else:
            pipeline = {constants.ID: user_id, constants.USOS_ID: self.getUsosId()}

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_USERS_INFO, pipeline)

        user_info_doc = await self.db[constants.COLLECTION_USERS_INFO].find_one(pipeline, USER_INFO_SKIP_FIELDS)

        if not user_info_doc:
            try:
                user_info_doc = await self.usos_user_info(user_id)
            except Exception as ex:
                await self.exc(ex, finish=False)

            if not user_info_doc:
                raise CallerError("Nie znaleziono danych dla użytkownika: {0}".format(user_id))

            # process faculties
            tasks_faculties = list()
            for position in user_info_doc['employment_positions']:
                tasks_faculties.append(self.api_faculty(position['faculty']['id']))

            await gen.multi(tasks_faculties)

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
                tasks_results = await gen.multi(tasks_courses)
                for course_doc in tasks_results:
                    courses_conducted.append({constants.COURSE_NAME: course_doc[constants.COURSE_NAME],
                                              constants.COURSE_ID: course_doc[constants.COURSE_ID],
                                              constants.TERM_ID: course_doc[constants.TERM_ID]})
            except Exception as ex:
                await self.exc(ex, finish=False)

            user_info_doc['course_editions_conducted'] = courses_conducted

            # if user has photo
            if 'has_photo' in user_info_doc and user_info_doc['has_photo']:
                photo_doc = await self.api_photo(user_info_doc[constants.ID])
                if photo_doc:
                    user_info_doc[constants.PHOTO_URL] = self.config.DEPLOY_API + '/users_info_photos/' + str(
                        photo_doc[constants.MONGO_ID])

            try:
                await self.db_insert(constants.COLLECTION_USERS_INFO, user_info_doc)
            except DuplicateKeyError as ex:
                logging.warning(ex)
            finally:
                user_info_doc = await self.api_user_info(user_info_doc[constants.ID])

        return user_info_doc
