# coding=UTF-8

from base64 import b64decode

import tornado.gen
import tornado.web
from bson.objectid import ObjectId

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import constants, settings, decorators
from commons.errors import ApiError
from commons.usosutils import usoshelper
from commons.usosutils import usosinstances


LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id',
    constants.HAS_PHOTO)


class UsersInfoByIdApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        try:
            user_info = yield self.api_user_info_id(user_id=user_info_id)

            if user_info:
                if constants.HAS_PHOTO in user_info and user_info[constants.HAS_PHOTO]:
                    user_info[constants.HAS_PHOTO] = settings.DEPLOY_API + '/users_info_photos/' + str(user_info[constants.HAS_PHOTO])

            else:
                raise ApiError('Szukamy informacji o Tobie w USOS.')

            self.success(user_info, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class UserInfoApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        '''
        :return:    join data from constants.COLLECTION_USERS and constants.COLLECTION_USERS_INFO and
                    school name from usosinstances.USOSINSTANCES
        '''

        try:
            user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: ObjectId(self.user_doc[constants.MONGO_ID])},
                LIMIT_FIELDS_USER)

            user_info = yield self.api_user_info()

            if not user_info or not user_info:
                raise ApiError('Poczekaj szukamy informacji o użytkowniku.')

            user_doc.update(user_info)

            # check if get photo needed
            if constants.HAS_PHOTO in user_doc and user_doc[constants.HAS_PHOTO]:
                user_doc[constants.HAS_PHOTO] = settings.DEPLOY_API + '/users_info_photos/' + str(user_info[constants.HAS_PHOTO])

            user_doc['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if
                                          usos[constants.USOS_ID] == user_doc[constants.USOS_ID]), None)

            self.success(user_doc, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class UserInfoPhotoApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, photo_id):

        try:
            if str(photo_id) == 'False' or str(photo_id) == 'True':
                raise ApiError('Nie podano odpowiedniego parametru photo_id')

            user_photo = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.MONGO_ID: ObjectId(photo_id)})

            self.set_header('Content-Type', 'image/jpeg')
            self.write(b64decode(user_photo['photo']))

        except Exception, ex:
            yield self.exc(ex)
