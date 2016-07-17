# coding=UTF-8

from base64 import b64decode

import tornado.gen
import tornado.web
from bson.objectid import ObjectId

from api.handlers.base import ApiHandler
from commons import constants, decorators
from commons import usosinstances
from commons.errors import ApiError

LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id',
    constants.PHOTO_URL, "{}.{}".format(constants.GOOGLE, constants.GOOGLE_NAME),
    "{}.{}".format(constants.GOOGLE, constants.GOOGLE_PICTURE),
    "{}.{}".format(constants.GOOGLE, constants.GOOGLE_EMAIL),
    "{}.{}".format(constants.FACEBOOK, constants.FACEBOOK_NAME),
    "{}.{}".format(constants.FACEBOOK, constants.FACEBOOK_PICTURE),
    "{}.{}".format(constants.FACEBOOK, constants.FACEBOOK_EMAIL))


class UsersInfoByIdApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        try:
            user_info_doc = yield self.api_user_info(user_id=user_info_id)

            if not user_info_doc:
                raise ApiError('Szukamy informacji o Tobie w USOS.')

            self.success(user_info_doc, cache_age=constants.SECONDS_2MONTHS)
        except Exception as ex:
            yield self.exc(ex)


class UserInfoApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
        :return:    join data from constants.COLLECTION_USERS and constants.COLLECTION_USERS_INFO and
                    school name from usosinstances.USOSINSTANCES
        """

        try:
            user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: ObjectId(self.get_current_user()[constants.MONGO_ID])},
                LIMIT_FIELDS_USER)

            user_info = yield self.api_user_info()

            if not user_info or not user_info or not user_doc:
                raise ApiError('Poczekaj szukamy informacji o użytkowniku.')

            user_doc.update(user_info)

            # check if get photo needed
            if constants.PHOTO_URL in user_doc and user_doc[constants.PHOTO_URL]:
                user_doc[constants.PHOTO_URL] = user_info[constants.PHOTO_URL]
            else:
                if constants.GOOGLE in user_doc and constants.GOOGLE_PICTURE in user_doc[constants.GOOGLE]:
                    user_doc[constants.PHOTO_URL] = user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE]
                if constants.FACEBOOK in user_doc and constants.FACEBOOK_PICTURE in user_doc[constants.FACEBOOK]:
                    user_doc[constants.PHOTO_URL] = user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE]

            user_doc['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if
                                          usos[constants.USOS_ID] == user_doc[constants.USOS_ID]), None)

            user_doc['theses'] = yield self.api_thesis()

            del(user_doc[constants.UPDATE_TIME])
            del(user_doc[constants.MONGO_ID])

            self.success(user_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            yield self.exc(ex)


class UserInfoPhotoApi(ApiHandler):
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

        except Exception as ex:
            yield self.exc(ex)
