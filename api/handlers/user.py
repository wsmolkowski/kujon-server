# coding=UTF-8

import logging
from base64 import b64decode

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants, settings
from commons.usosutils import usoshelper
from commons.usosutils import usosinstances

LIMIT_FIELDS = (
    'first_name', 'last_name', 'email', 'id', 'student_number', 'student_status', 'has_photo', 'student_programmes',
    'user_type','has_photo')
LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id')


class UsersInfoByIdApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        parameters = yield self.get_parameters()
        if not parameters:
            return

        user_info = yield self.db.users_info.find_one({constants.ID: user_info_id}, LIMIT_FIELDS)
        if user_info:
            # check if user has account in kujon
            user = yield self.db[constants.COLLECTION_USERS].find_one({'id': ObjectId(user_info[constants.MONGO_ID])})
            if not user:
                user_info[constants.USER_ID] = None
            else:
                user_info[constants.USER_ID] = user[constants.USER_ID]

            # change student status value to name
            user_info['student_status'] = usoshelper.dict_value_student_status(user_info['student_status'])
        else:
            self.error('Please hold on we are looking your USOS user information.')
            return

        #show url to photo
        if user_info['has_photo']:
            user_info['has_photo'] = settings.DEPLOY_API + '/api/users_info_photos/' + str(user_info['has_photo'])

        self.success(user_info)


class UserInfoApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()
        if not parameters:
            return

        user = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(parameters[constants.MONGO_ID])},
                                                                  LIMIT_FIELDS_USER)
        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.MONGO_ID])}, LIMIT_FIELDS)

        if not user_info:
            self.error('Poczekaj szukamy informacji o użytkowniku..')
            return

        if 'email' in user_info:
            user_info['user_email'] = user_info.pop('email')

        user.update(user_info)

        # remove unneccecary fields
        user.pop('update_time')

        user['student_status'] = usoshelper.dict_value_student_status(user['student_status'])

        # add school name from usosinstances based on usos_id
        user['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if usos[constants.USOS_ID] == user[constants.USOS_ID]), None)

        if not user:
            self.error('Poczekaj szukamy informacji o użytkowniku.')
        else:
            self.success(user)


class UserInfoPhotoApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, photo_id):

        yield self.get_parameters()

        try:
            user_photo = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.MONGO_ID: ObjectId(photo_id)})
            self.set_header('Content-Type', 'image/jpeg')
            self.write(b64decode(user_photo['photo']))
            
        except Exception, ex:
            logging.exception('Exception while getting user photo: {0}'.format(ex.message))
            self.error('Niepoprawny numer zdjęcia.')
