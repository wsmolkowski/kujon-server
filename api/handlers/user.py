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


LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id')


class UsersInfoByIdApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        try:
            user_info = yield self.api_user_info_id(user_id=user_info_id)

            if user_info:
                if 'has_photo' in user_info and user_info['has_photo']:
                    user_info['has_photo'] = settings.DEPLOY_API + '/users_info_photos/' + str(user_info['has_photo'])

                if 'student_status' in user_info:
                    user_info['student_status'] = usoshelper.dict_value_student_status(user_info['student_status'])
            else:
                raise ApiError('Szukamy informacji o Tobie w USOS.')

            self.success(user_info, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class UserInfoApi(BaseHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        '''
        :return:    join data from constants.COLLECTION_USERS and constants.COLLECTION_USERS_INFO
        '''

        try:
            user = yield self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: ObjectId(self.user_doc[constants.MONGO_ID])},
                LIMIT_FIELDS_USER)

            user_info = yield self.api_user_info()

            if not user_info:
                raise ApiError('Poczekaj szukamy informacji o użytkowniku.')

            user.update(user_info)

            user['student_status'] = usoshelper.dict_value_student_status(user['student_status'])

            # add school name from usosinstances based on usos_id
            user['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if
                                      usos[constants.USOS_ID] == user[constants.USOS_ID]), None)

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
