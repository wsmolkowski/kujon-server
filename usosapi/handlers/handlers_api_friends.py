import tornado.web
from bson.objectid import ObjectId

import usosapi.helpers
from handlers_api import BaseHandler
from usosapi import constants
from usosapi.mixins.JSendMixin import JSendMixin


class FriendsAddApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_to_add_info_id):

        user_doc, usos_doc = yield self.get_parameters()

        friend_doc = yield self.db[constants.COLLECTION_FRIENDS].find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID]),
                                                                            constants.USOS_ID: usos_doc[constants.USOS_ID],
                                                                            constants.FRIEND_ID: user_to_add_info_id})
        if not friend_doc:
            result = {}
            result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
            result[constants.USER_ID] = ObjectId(user_doc[constants.USER_ID])
            result[constants.FRIEND_ID] = str(user_to_add_info_id)
            friend_doc = self.db[constants.COLLECTION_FRIENDS].insert(result)

        if friend_doc:
            self.redirect("/friends/suggestions?added={0}".format(user_to_add_info_id))


class FriendsRemoveApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_to_remove_info_id):

        user_doc, usos_doc = yield self.get_parameters()

        friend_doc = yield self.db[constants.COLLECTION_FRIENDS].remove({constants.USER_ID: ObjectId(user_doc[constants.USER_ID]),
                                                                            constants.USOS_ID: usos_doc[constants.USOS_ID],
                                                                            constants.FRIEND_ID: user_to_remove_info_id})
        if friend_doc:
            self.redirect("/friends?removed={0}".format(user_to_remove_info_id))
        else:
            self.redirect("/friends?failed_removed={0}".format(user_to_remove_info_id))



class FriendsSuggestionsApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()
        user_info = yield self.db.users_info.find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})


        courses = {}
        course_doc = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})

        for term in course_doc['course_editions']:
            for course in course_doc['course_editions'][term]:
                courses[course[constants.COURSE_ID]] = course

        suggested_participants = {}
        for course in courses:
            course_participants = yield self.db[constants.COLLECTION_PARTICIPANTS].find_one(
                {constants.COURSE_ID: course, constants.TERM_ID: courses[course][constants.TERM_ID],
                 constants.USOS_ID: usos_doc[constants.USOS_ID]})

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
                poz = usosapi.helpers.in_dictlist((constants.FRIEND_ID, participant_id), friends_added)
                if poz:
                    continue

                # count how many courses have together
                if participant_id in suggested_participants:
                    suggested_participants[participant_id]['count'] += 1
                else:
                    suggested_participants[participant_id]=participant
                    suggested_participants[participant_id]['count'] = 1

        suggested_participants = suggested_participants.values()

        # TODO: add sort by column id
        # TODO: show message on add friends

        if not suggested_participants:
            self.error("Please hold on we are looking your friends sugestions.")
        else:
            self.success(suggested_participants)


class FriendsApi(BaseHandler, JSendMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user_doc, usos_doc = yield self.get_parameters()
        user_info = yield self.db.users_info.find_one({constants.USER_ID: ObjectId(user_doc[constants.USER_ID])})


        friends = []
        cursor = self.db[constants.COLLECTION_FRIENDS].find()
        while (yield cursor.fetch_next):
            friends.append(cursor.next_object())

        self.success(friends)
