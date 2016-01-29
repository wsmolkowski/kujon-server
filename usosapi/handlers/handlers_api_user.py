import logging
from datetime import datetime

import motor
import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.usosupdater import USOSUpdater


class UserHandler(BaseHandler):

    def loadUserData(self,user_doc):

        # load courseeditions
        import urllib2
        # response = urllib2.urlopen("http://localhost:8888/api/courseseditions?{0}")
        # response = http.fetch("/api/courseseditions?{0}".format(self.auth_uri))
        # print response

        # for each courseeditions load courses and grades

        pass

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.validate_parameters(4)
        parameters = self.get_parameters()
        try:
            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: parameters.mobile_id,
                                                 constants.ACCESS_TOKEN_SECRET: parameters.access_token_secret,
                                                 constants.ACCESS_TOKEN_KEY: parameters.access_token_key})
        except Exception, ex:
                raise tornado.web.HTTPError(500, "Exception while fetching user data %s".format(ex))

        # TODO: to nie powinno dzilac jak nie ma usera
        usos = yield self.db.usosinstances.find_one({constants.USOS_ID: user_doc[constants.USOS_ID]})
        self.validate_usos(usos, parameters)

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

            logging.info("saved new user in database: {0}".format(user_doc))
            user_doc = result

        else:
            logging.info("user data fetched from database {0}".format(user_doc))

        self.write(json_util.dumps(user_doc))
        self.loadUserData(user_doc)