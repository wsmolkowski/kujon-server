# coding=UTF-8

from base64 import b64decode

import tornado.web
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants
from commons.usosutils import usosinstances

LIMIT_FIELDS = (
    'first_name', 'last_name', 'email', 'id', 'student_number', 'student_status', 'has_photo', 'student_programmes',
    'user_type')
LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id')


class UsersInfoByIdApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        # parameters = yield self.get_parameters(usos_paired=True)

        user_info = yield self.db.users_info.find_one({constants.USER_INFO_ID: user_info_id}, LIMIT_FIELDS)
        if user_info:
            user = yield self.db[constants.COLLECTION_USERS].find_one({'id': ObjectId(user_info[constants.ID])})
            result = list()
            result.append(user)
            result.append(user_info)
            self.success(result)
        else:
            self.error(u"Please hold on we are looking your USOS user information.")


class UserInfoApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        user = yield self.db[constants.COLLECTION_USERS].find_one({constants.ID: ObjectId(parameters[constants.ID])},
                                                                  LIMIT_FIELDS_USER)
        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.ID])}, LIMIT_FIELDS)

        if not user_info:
            self.error(u"Poczekaj szukamy informacji o użytkowniku..")
            return

        user_info['user_email'] = user_info.pop('email')

        user.update(user_info)

        # remove unneccecary fields
        user.pop('update_time')

        # change student status value to name
        if user['student_status'] == 0:
            user['student_status'] = u"brak"
        elif user['student_status'] == 1:
            user['student_status'] = u"nieaktywny student"
        elif user['student_status'] == 2:
            user['student_status'] = u"aktywny student"

        # change description to only polish
        for program in user['student_programmes']:
            program['programme']['description'] = program['programme']['description']['pl']

        # add school name from usosinstances based on usos_id
        user['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if usos[constants.USOS_ID] == user[constants.USOS_ID]), None)

        if not user:
            self.error(u"Poczekaj szukamy informacji o użytkowniku..")
        else:
            self.success(user)


class UserInfoPhotoApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, photo_id):

        try:
            user_photo = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.ID: ObjectId(photo_id)})
            if user_photo:
                self.set_header("Content-Type", "image/jpeg")
                self.write(b64decode(user_photo['photo']))
        except Exception:
            self.error(u"Niepoprawny numer zdjęcia..")
