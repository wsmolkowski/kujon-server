import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.mixins.JSendMixin import JSendMixin

LIMIT_FIELDS = ('first_name', 'last_name', 'email', 'id', 'student_number', 'student_status', 'photo_urls', 'student_programmes')


class UsersInfoByIdApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, users_info_id):

        user_doc, usos_doc = yield self.get_parameters()

        user_info = yield self.db.users_info.find_one({constants.USER_USOS_ID: users_info_id}, LIMIT_FIELDS)

        if not user_info:
            self.error("Please hold on we are looking your USOS user information.")
        else:
            self.success(user_info)


class UserInfoapi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        user_info = yield self.db.users_info.find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])}, LIMIT_FIELDS)


        if not user_info:
            self.error("Please hold on we are looking your USOS user information.")
        else:
            self.success(user_info)
