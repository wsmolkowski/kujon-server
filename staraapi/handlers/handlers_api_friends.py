import tornado.web
from bson.objectid import ObjectId

from handlers_api import BaseHandler
from staracommon import constants, helpers


class FriendsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()

        friends = []
        friends_returned = []
        # TODO: ograniczyc wynik zwrcany do 3 pol: imie, nzwisko, id
        pipeline = [{'$match': {'user_id': ObjectId(parameters[constants.ID])}},
                    {'$lookup': {'from': 'users_info', 'localField': 'friend_id', 'foreignField': 'id',
                                 'as': 'users_info'}}]

        cursor = self.db[constants.COLLECTION_FRIENDS].aggregate(pipeline)
        if cursor:
            while (yield cursor.fetch_next):
                friends.append(cursor.next_object())

            for elem in friends:
                new_elem = {}
                new_elem['user_id'] = elem['friend_id']
                user_info = elem['users_info'].pop()
                new_elem['first_name'] = user_info['first_name']
                new_elem['last_name'] = user_info['last_name']
                new_elem['sex'] = user_info['sex']
                friends_returned.append(new_elem)

            self.success(friends_returned)
        else:
            self.error("Please hold on we are looking your friends..")

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, user_info_id):

        parameters = yield self.get_parameters()

        friend_doc = yield self.db[constants.COLLECTION_FRIENDS].find_one({constants.USER_ID: ObjectId(parameters[
                                                                                                           constants.ID]),
                                                                           constants.FRIEND_ID: user_info_id})
        if not friend_doc:

            # check if user_info exists
            user_info = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_INFO_ID: user_info_id,
                                                                                 constants.USOS_ID: parameters[
                                                                                     constants.USOS_ID]})

            if user_info:
                result = {}
                result[constants.USOS_ID] = parameters[constants.USOS_ID]
                result[constants.USER_ID] = ObjectId(parameters[constants.ID])
                result[constants.FRIEND_ID] = str(user_info_id)
                friend_doc = self.db[constants.COLLECTION_FRIENDS].insert(result)
                if friend_doc:
                    self.success(user_info_id)
                else:
                    self.fail(user_info_id)
            else:
                self.fail(user_info_id)
        else:
            self.fail(user_info_id)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self, user_info_id):

        parameters = yield self.get_parameters()

        friend_in_db = yield self.db[constants.COLLECTION_FRIENDS].find_one({constants.USER_ID: ObjectId(parameters[
                                                                                                             constants.ID]),
                                                                             constants.FRIEND_ID: user_info_id})
        if friend_in_db:
            friend_doc = yield self.db[constants.COLLECTION_FRIENDS].remove({constants.USER_ID: ObjectId(parameters[
                                                                                                             constants.ID]),
                                                                             constants.FRIEND_ID: user_info_id})
            if friend_doc:
                self.success(user_info_id)
        else:
            self.fail(user_info_id)


class FriendsSuggestionsApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        parameters = yield self.get_parameters()
        user_info = yield self.db.users_info.find_one({constants.USER_ID: ObjectId(parameters[constants.ID])})

        courses = {}
        suggested_participants = {}

        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.ID])})
        if course_doc:
            for term in course_doc['course_editions']:
                for course in course_doc['course_editions'][term]:
                    courses[course[constants.COURSE_ID]] = course

            for course in courses:
                course_participants = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
                    {constants.COURSE_ID: course, constants.TERM_ID: courses[course][constants.TERM_ID],
                     constants.USOS_ID: parameters[constants.USOS_ID]})

                if not course_participants:
                    continue

                # TODO: change to metod in dao??
                friends_added = []
                cursor = self.db[constants.COLLECTION_FRIENDS].find()
                while (yield cursor.fetch_next):
                    friends_added.append(cursor.next_object())

                for participant in course_participants[constants.PARTICIPANTS]:
                    participant_id = participant[constants.USER_ID]

                    # checking if participant is not current logged user
                    if int(user_info[constants.USER_INFO_ID]) == participant_id:
                        continue

                    # checking if participant is allready added
                    poz = helpers.in_dictlist((constants.FRIEND_ID, participant_id), friends_added)
                    if poz:
                        continue
                    del participant[constants.USER_INFO_ID]
                    # count how many courses have together
                    if participant_id in suggested_participants:
                        suggested_participants[participant_id]['count'] += 1
                    else:
                        suggested_participants[participant_id] = participant
                        suggested_participants[participant_id]['count'] = 1

            suggested_participants = suggested_participants.values()

            # TODO: show message on add friends

        if not suggested_participants:
            self.error("Please hold on we are looking your friends sugestions..")
        else:
            self.success(suggested_participants)
