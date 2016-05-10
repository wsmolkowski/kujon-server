# coding=UTF-8

from base64 import b64decode

import tornado.gen
import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants, settings, decorators
from commons.errors import ApiError
from commons.usosutils import usoshelper
from commons.usosutils import usosinstances

LIMIT_FIELDS = (
    'first_name', 'last_name', 'email', 'id', 'student_number', 'student_status', 'has_photo', 'student_programmes',
    'user_type', 'has_photo')
LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id')


class UsersInfoByIdApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        try:
            user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: user_info_id},
                                                                                LIMIT_FIELDS)
            if user_info:
                # check if user has account in kujon
                user = yield self.db[constants.COLLECTION_USERS].find_one(
                    {'id': ObjectId(user_info[constants.MONGO_ID])})
                if not user:
                    user_info[constants.USER_ID] = None
                else:
                    user_info[constants.USER_ID] = user[constants.USER_ID]

                # change student status value to name
                user_info['student_status'] = usoshelper.dict_value_student_status(user_info['student_status'])
            else:
                self.error('Szukamy informacji o Tobie w USOS.')
                return

            # show url to photo
            if user_info['has_photo']:
                user_info['has_photo'] = settings.DEPLOY_API + '/users_info_photos/' + str(user_info['has_photo'])

            self.success(user_info, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class UserInfoApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            user = yield self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: ObjectId(self.user_doc[constants.MONGO_ID])},
                LIMIT_FIELDS_USER)
            user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
                {constants.USER_ID: ObjectId(self.user_doc[constants.MONGO_ID])}, LIMIT_FIELDS)

            if not user_info:
                raise ApiError('Poczekaj szukamy informacji o użytkowniku.')

            if 'email' in user_info:
                user_info['user_email'] = user_info.pop('email')

            user.update(user_info)

            user['student_status'] = usoshelper.dict_value_student_status(user['student_status'])

            # add school name from usosinstances based on usos_id
            user['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if
                                      usos[constants.USOS_ID] == user[constants.USOS_ID]), None)

            if not user:
                self.error('Poczekaj szukamy informacji o użytkowniku.')
            else:
                self.success(user, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class UserInfoPhotoApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, photo_id):

        try:
            user_photo = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.MONGO_ID: ObjectId(photo_id)})
            self.set_header('Content-Type', 'image/jpeg')
            self.write(b64decode(user_photo['photo']))

        except Exception, ex:
            yield self.exc(ex)
