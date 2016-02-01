import tornado.web
from bson import json_util

from handlers_api import BaseHandler
from usosapi import constants


class Parameters:
    def __init__(self, user_doc, usos_doc):
        self.user_doc = user_doc
        self.usos_doc = usos_doc


class FriendsSuggestionsApi(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()

        '''
        data = yield self.db.curses_editions.find_one({'user_id': parameters.user_doc[constants.ID]},
                                                      ('course_editions', ))
        '''

        participants = []
        cursor = self.db[constants.COLLECTION_PARTICIPANTS].find()
        while (yield cursor.fetch_next):
            participants.append(cursor.next_object())
        self.write(json_util.dumps(participants))