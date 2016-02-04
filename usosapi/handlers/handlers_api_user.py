import tornado.web
from bson import json_util
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
        if not user_info:
            self.fail("Could not obtain usos user info for {0}".format(user_doc[constants.USER_ID]))
        else:
            self.success(json_util.dumps(user_info))
