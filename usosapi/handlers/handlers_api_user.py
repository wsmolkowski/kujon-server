import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.mixins.JSendMixin import JSendMixin


class UserApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        user_info = yield self.db.users_info.find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})
        user_info.pop(constants.ID)
        user_info.pop(constants.USER_ID)

        if not user_info:
            self.error("Please hold on we are looking your USOS info.")
        else:
            self.success(user_info)
