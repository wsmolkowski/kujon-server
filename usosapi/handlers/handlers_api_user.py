import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants


class UserApi(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        # przeniesc cala sekcje do oddzielnej metody najlpeiej do base handler bo to sie powtarza
        parameters = self.get_parameters()
        try:
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})
            if user_doc:
                    usos = yield self.db.usosinstances.find_one({constants.USOS_ID: user_doc[constants.USOS_ID]})
                    self.validate_usos(usos, parameters)
        except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching user data (0)".format(ex.message))
        # do tego miejsca

        user_info = yield self.db.users_info.find_one({constants.USER_ID: user_doc[constants.ID]})

        self.write(json_util.dumps(user_info))
