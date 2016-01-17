import tornado.web
from bson import json_util

import handlers_api


class UsosesHandler(handlers_api.BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        # TODO: params list verfication
        # TODO: jak zabezpieczyc ta metode
        # self.validate_parameters(4)
        # parameters = self.get_parameters()

        # usoses = yield self.db.usosinstances.find()
        cursor = self.db.usosinstances.find()
        usoses = yield cursor.to_list(None)
        self.write(json_util.dumps(usoses))


