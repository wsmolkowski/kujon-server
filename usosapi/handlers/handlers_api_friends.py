import logging

from usosapi import constants
import tornado.web
from bson import json_util

from handlers_api import BaseHandler


class Parameters:
    def __init__(self, user_doc, usos_doc):
        self.user_doc = user_doc
        self.usos_doc = usos_doc


class FriendsSuggestionsApi(BaseHandler):
    @tornado.gen.coroutine
    def get_parameters(self):

        user_doc = self.get_current_user()

        if not user_doc:
            # usos_id = self.get_argument(constants.USOS_ID, default=None, strip=True)
            mobile_id = self.get_argument(constants.MOBILE_ID, default=None, strip=True)
            atk = self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True)
            ats = self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True)

            user_doc = yield self.db.users.find_one({constants.MOBILE_ID: mobile_id,
                                             constants.ACCESS_TOKEN_SECRET: atk,
                                             constants.ACCESS_TOKEN_KEY: ats})

        usos_doc = self.get_usos(user_doc[constants.USOS_ID])

        raise tornado.gen.Return(Parameters(user_doc, usos_doc))

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        '''
        data = yield self.db.curses_editions.find_one({'user_id': parameters.user_doc[constants.ID]},
                                                      ('course_editions', ))
        '''

        participants = []
        cursor = self.db.participants.find()
        while (yield cursor.fetch_next):
            participants.append(cursor.next_object())
        self.write(json_util.dumps(participants))