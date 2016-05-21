# coding=UTF-8

import tornado.gen
import tornado.web
from bson.objectid import ObjectId

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import constants, helpers, decorators


class FriendsApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        friends = []
        friends_returned = []
        pipeline = [{'$match': {'user_id': ObjectId(self.user_doc[constants.MONGO_ID])}},
                    {'$lookup': {'from': 'users_info', 'localField': 'friend_id', 'foreignField': 'id',
                                 'as': 'users_info'}}]

        cursor = self.db[constants.COLLECTION_FRIENDS].aggregate(pipeline)
        if cursor:
            while (yield cursor.fetch_next):
                friends.append(cursor.next_object())

            for elem in friends:
                new_elem = dict()
                new_elem['user_id'] = elem['friend_id']
                user_info = elem['users_info'].pop()
                new_elem['first_name'] = user_info['first_name']
                new_elem['last_name'] = user_info['last_name']
                new_elem['sex'] = user_info['sex']
                friends_returned.append(new_elem)

            self.success(friends_returned)
        else:
            self.error("Poczekaj szukamy przyjaciół.")

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, user_info_id):

        friend_doc = yield self.db[constants.COLLECTION_FRIENDS].find_one({constants.USER_ID: ObjectId(self.user_doc[
                                                                                                           constants.MONGO_ID]),
                                                                           constants.FRIEND_ID: user_info_id})
        if not friend_doc:

            # check if user_info exists
            user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: user_info_id,
                                                                                 constants.USOS_ID: self.user_doc[
                                                                                     constants.USOS_ID]})

            if user_info:
                result = dict()
                result[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
                result[constants.USER_ID] = ObjectId(self.user_doc[constants.MONGO_ID])
                result[constants.FRIEND_ID] = str(user_info_id)
                friend_doc = self.db[constants.COLLECTION_FRIENDS].insert(result)
                if friend_doc:
                    self.success(user_info_id)
                else:
                    self.fail(message=user_info_id)
            else:
                self.fail(message=user_info_id)
        else:
            self.fail(message=user_info_id)

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self, user_info_id):
        friend_in_db = yield self.db[constants.COLLECTION_FRIENDS].find_one({constants.USER_ID: ObjectId(self.user_doc[
                                                                                                             constants.MONGO_ID]),
                                                                             constants.FRIEND_ID: user_info_id})
        if friend_in_db:
            friend_doc = yield self.db[constants.COLLECTION_FRIENDS].remove({constants.USER_ID: ObjectId(self.user_doc[
                                                                                                             constants.MONGO_ID]),
                                                                             constants.FRIEND_ID: user_info_id})
            if friend_doc:
                self.success(user_info_id)
        else:
            self.fail(message=user_info_id)


class FriendsSuggestionsApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_info = yield self.api_user_info(None)

        courses = {}
        suggested_participants = {}

        courses_editions_doc = yield self.api_courses_editions()

        if courses_editions_doc:
            for term in courses_editions_doc['course_editions']:
                for course in courses_editions_doc['course_editions'][term]:
                    courses[course[constants.COURSE_ID]] = course

            for course in courses:
                course_participants = yield self.api_course_edition(course, courses[course][constants.TERM_ID])
                if not course_participants:
                    continue

                friends_added = list()
                cursor = self.db[constants.COLLECTION_FRIENDS].find()
                while (yield cursor.fetch_next):
                    friends_added.append(cursor.next_object())

                for participant in course_participants[constants.PARTICIPANTS]:
                    participant_id = participant[constants.USER_ID]

                    # checking if participant is not current logged user
                    if user_info[constants.ID] == participant_id:
                        continue

                    # checking if participant is allready added
                    poz = helpers.in_dictlist((constants.FRIEND_ID, participant_id), friends_added)
                    if poz:
                        continue
                    del participant[constants.ID]
                    # count how many courses have together
                    if participant_id in suggested_participants:
                        suggested_participants[participant_id]['count'] += 1
                    else:
                        suggested_participants[participant_id] = participant
                        suggested_participants[participant_id]['count'] = 1

            suggested_participants = suggested_participants.values()

        if not suggested_participants:
            self.error("Poczekaj szukamy sugerowanych przyjaciół.")
        else:
            # sort by count descending and limit to 10 records
            suggested_participants = sorted(suggested_participants, key=lambda k: k['count'], reverse=True)
            self.success(suggested_participants[:10])
