import logging
from datetime import datetime

import motor
import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.usosupdater import USOSUpdater


class UserHandler(BaseHandler):

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

        if not user_doc or not constants.USER_USOS_ID in user_doc:
            try:
                updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY],
                                      usos[constants.CONSUMER_SECRET],
                                      parameters.access_token_key, parameters.access_token_secret)

                result = updater.request_user_info()
            except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching USOS data for user info: {0}".format(ex.message))

            result[constants.USER_USOS_ID] = result.pop('id')
            result[constants.USOS_ID] = usos[constants.USOS_ID]
            result[constants.MOBILE_ID] = parameters.mobile_id
            result[constants.ACCESS_TOKEN_SECRET] = parameters.access_token_secret
            result[constants.ACCESS_TOKEN_KEY] = parameters.access_token_key
            result[constants.CREATED_TIME] = datetime.now()

            if not user_doc:
                user_doc = yield motor.Op(self.db.users.insert, result)
            else:
                user_doc = yield self.db.users.update({'_id': user_doc['_id']}, result)

            logging.info("saved new user in database: {0}".format(user_doc))
            user_doc = result

        else:
            logging.info("user data fetched from database {0}".format(user_doc))

        self.write(json_util.dumps(user_doc))
