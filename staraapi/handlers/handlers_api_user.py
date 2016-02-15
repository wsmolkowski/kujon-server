from base64 import b64decode

import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from staraapi import constants

LIMIT_FIELDS = ('first_name', 'last_name', 'email', 'id', 'student_number', 'student_status', 'has_photo', 'student_programmes')

class UsersInfoByIdApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        parameters = yield self.get_parameters()

        user_info = yield self.db.users_info.find_one({constants.USER_INFO_ID: user_info_id}, LIMIT_FIELDS)
        if user_info:
            user = yield self.db[constants.COLLECTION_USERS].find_one({'id': ObjectId(user_info[constants.ID])})
            result = []
            result.append(user)
            result.append(user_info)
            self.success(result)
        else:
            user = {}
            self.error("Please hold on we are looking your USOS user information.")

class UserInfoapi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        user = yield self.db[constants.COLLECTION_USERS].find_one({constants.ID: ObjectId(parameters[constants.ID])})
        user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: ObjectId(parameters[constants.ID])}, LIMIT_FIELDS)

        result = []
        result.append(user)
        result.append(user_info)

        if not user:
            self.error("Please hold on we are looking your USOS/user information.")
        else:
            self.success(result)

class UserInfoPhotoApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_id):

        parameters = yield self.get_parameters()

        user_photo = yield self.db[constants.COLLECTION_PHOTOS].find_one({constants.USER_ID: user_id})
        if user_photo:
            self.set_header("Content-Type", "image/jpeg")
            self.write(b64decode(user_photo['photo']))
