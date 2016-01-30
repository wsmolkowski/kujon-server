import logging

import motor
import tornado.web
from bson import json_util

from handlers_api import BaseHandler

class FriendsSuggestionsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        participants = []
        cursor = self.db.participants.find()
        while (yield cursor.fetch_next):
            participants.append(cursor.next_object())
        print json_util.dumps(participants)
        self.write(json_util.dumps(participants))