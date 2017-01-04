# coding=utf-8

import logging

from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from tornado import gen

from commons import usoshelper
from commons.constants import fields, collections
from commons.errors import ApiError
from commons.mixins.DaoMixin import DaoMixin

USER_INFO_SKIP_FIELDS = {'email_access': False,
                         'employment_functions': False, fields.CREATED_TIME: False, 'email': False,
                         'usos_id': False, fields.UPDATE_TIME: False, fields.MONGO_ID: False}


class ApiUserMixin(DaoMixin):
    async def api_photo(self, user_info_id):
        pipeline = {fields.ID: user_info_id}
        if self.do_refresh():
            await self.db_remove(collections.PHOTOS, pipeline)

        photo_doc = await self.db[collections.PHOTOS].find_one(pipeline)

        if not photo_doc:
            try:
                photo_doc = await self.usosCall(
                    path='services/photos/photo',
                    arguments={
                        'user_id': user_info_id,
                    })

                photo_doc[fields.ID] = user_info_id

                photo_id = await self.db_insert(collections.PHOTOS, photo_doc)
                photo_doc = await self.db[collections.PHOTOS].find_one(
                    {fields.MONGO_ID: ObjectId(photo_id)})
            except Exception as ex:
                logging.exception(ex)
        return photo_doc

    async def usos_user_info(self, user_id=None):
        '''
        :param user_id:
        :return: parsed usos user info
        '''

        fields = 'id|staff_status|first_name|last_name|student_status|sex|email|email_url|has_email|email_access|student_programmes|student_number|titles|has_photo|course_editions_conducted|office_hours|interests|room|employment_functions|employment_positions|homepage_url'

        if user_id:
            result = await self.usosCall(path='services/users/user',
                                         arguments={'fields': fields, 'user_id': user_id})
        else:
            result = await self.usosCall(path='services/users/user', arguments={'fields': fields})

        if not result:
            raise ApiError('Problem z pobraniem danych z USOS na temat użytkownika.')

        # strip empty values
        if 'homepage_url' in result and result['homepage_url'] == "":
            result['homepage_url'] = None

        if 'student_status' in result:
            result['student_status'] = usoshelper.dict_value_student_status(result['student_status'])

        # change staff_status to dictionary
        result['staff_status'] = usoshelper.dict_value_staff_status(result['staff_status'])

        return result

    async def user_info(self, user_id=None):
        '''
        build user info based on usos_info, faculties, course_editions_conducted and has_photo
        :param user_id:
        :return:
        '''

        user_info_doc = await self.usos_user_info(user_id)

        # process faculties
        tasks_faculties = list()
        for position in user_info_doc['employment_positions']:
            tasks_faculties.append(self.api_faculty(position['faculty']['id']))

        await gen.multi(tasks_faculties)

        # process course_editions_conducted

        courses_conducted = []
        tasks_courses = list()
        courses = list()

        courses_editions = await self.api_courses_editions()

        for course_conducted in user_info_doc['course_editions_conducted']:
            course_id, term_id = course_conducted['id'].split('|')
            if course_id not in courses:
                courses.append(course_id)
                tasks_courses.append(self.api_course_term(course_id, term_id, extra_fetch=False, log_exception=False,
                                                          courses_editions=courses_editions))

        try:
            tasks_results = await gen.multi(tasks_courses)
            for course_doc in tasks_results:
                if not course_doc:
                    continue
                courses_conducted.append({fields.COURSE_NAME: course_doc[fields.COURSE_NAME],
                                          fields.COURSE_ID: course_doc[fields.COURSE_ID],
                                          fields.TERM_ID: course_doc[fields.TERM_ID]})
        except Exception as ex:
            await self.exc(ex, finish=False)

        user_info_doc['course_editions_conducted'] = courses_conducted

        # if user has photo
        if 'has_photo' in user_info_doc and user_info_doc['has_photo']:
            photo_doc = await self.api_photo(user_info_doc[fields.ID])
            if photo_doc:
                user_info_doc[fields.PHOTO_URL] = self.config.DEPLOY_API + '/users_info_photos/' + str(
                    photo_doc[fields.MONGO_ID])

        return user_info_doc

    async def updated_user_doc(self):
        '''
        update user collection with USOS_INFO_ID and USOS_USER_ID
        :return:
        '''

        user_info_doc = await self.user_info()
        if user_info_doc:
            user_doc = await self.db_find_user()

            if not user_doc:
                return user_info_doc  # TypeError: 'NoneType' object does not support item assignment

            user_doc[fields.USOS_USER_ID] = user_info_doc[fields.ID]

            await self.db_update_user(user_doc[fields.MONGO_ID], user_doc)

        return user_info_doc

    async def api_user_usos_info(self):
        '''
        get usos user info for current user (without usos_user_id)
        :return:
        '''

        user_usos_id = await self.db_user_usos_id()
        if user_usos_id:
            return await self.api_user_info(user_usos_id)

            # if user_info_doc and fields.USOS_USER_ID not in user_info_doc:
            #     ''' update for old users '''
            #     user_info_doc = await self.updated_user_doc()
            #
            # return user_info_doc

        return await self.updated_user_doc()

    async def api_user_info(self, user_id):
        '''
        get usos user info for id
        :param user_id:
        :return:
        '''

        pipeline = {fields.ID: user_id, fields.USOS_ID: self.getUsosId()}

        if self.do_refresh() and user_id:
            await self.db_remove(collections.USERS_INFO, pipeline)

        user_info_doc = await self.db[collections.USERS_INFO].find_one(pipeline, USER_INFO_SKIP_FIELDS)

        if not user_info_doc:
            try:
                user_info_doc = await self.user_info(user_id)
                await self.db_insert(collections.USERS_INFO, user_info_doc)

                user_info_doc = await self.db[collections.USERS_INFO].find_one(pipeline, USER_INFO_SKIP_FIELDS)

            except DuplicateKeyError as ex:
                logging.debug(ex)

        return user_info_doc
