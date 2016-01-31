import tornado.web
from bson import json_util
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants


class UserApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        user_info = yield self.db.users_info.find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})
        if not user_info:
            pass    # TODO: return json with custom message

        self.write(json_util.dumps(user_info))
