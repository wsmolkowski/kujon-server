import tornado.web
from bson import json_util
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from usosapi import constants
from usosapi.mixins.JSendMixin import JSendMixin


class Parameters:
    def __init__(self, user_doc, usos_doc):
        self.user_doc = user_doc
        self.usos_doc = usos_doc


class FriendsSuggestionsApi(BaseHandler, JSendMixin):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()


        # for each course, terms in courses_editions
        # select courses, id, _id from courses
        # for each course select participants
        # for each participantsbiuld sugeested_participant
        # return sugested participant

        participants = {}
        pipeline = [{'$match': {'user_id' : ObjectId("56ae5a793d7821151c33954d")}},
                   {'$lookup': {'from': 'courses_participants','localField': 'course_id', 'foreignField': 'course_id', 'as': 'participants'}},
                   {'$project': {'participants.participants': 1}}]
        cursor = self.db[constants.COLLECTION_COURSES].aggregate(pipeline)
        while (yield cursor.fetch_next):
            participants_collections = cursor.next_object()
            for friend in participants_collections['participants']:
                user_id = friend['id']
                if user_id in participants:
                    participants[user_id]['count']=int(participants[user_id]['count']) + 1
                else:
                    participants[user_id]=friend
                    participants[user_id]['count'] = 1

        self.success(json_util.dumps(participants))