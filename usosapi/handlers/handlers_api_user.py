import logging
from datetime import datetime

import motor
import tornado.web
from bson import json_util

from usosapi import constants
from handlers_api import BaseHandler
from usosapi.usosupdater import USOSUpdater


class UserHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)

        parameters = self.get_parameters()

        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: parameters.usos_id})
        self.validate_usos(usos, parameters)

        user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})

        if not user_doc:
            try:
                print usos[constants.URL], usos[constants.CONSUMER_KEY], usos[
                    constants.CONSUMER_SECRET], \
                    parameters.access_token_key, parameters.access_token_secret
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)

                result = updater.request_user_info()
            except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching USOS data for user info %s".format(ex))

            result[constants.USER_USOS_ID] = result.pop('id')
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.ACCESS_TOKEN_SECRET] = parameters.access_token_secret
            result[constants.ACCESS_TOKEN_KEY] = parameters.access_token_key
            result[constants.CREATED_TIME] = datetime.now()

            user_doc = yield motor.Op(self.db.users.insert, result)

            logging.debug("saved new user in database: {0}".format(user_doc))
            user_doc = result

        else:
            logging.debug("user data fetched from database {0}".format(user_doc))

        self.write(json_util.dumps(user_doc))
