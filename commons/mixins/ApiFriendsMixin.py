# coding=UTF-8

from tornado import gen

from commons import constants, helpers
from commons.errors import ApiError
from commons.mixins.DaoMixin import DaoMixin


class ApiMixinFriends(DaoMixin):

    @gen.coroutine
    def api_friends(self):
        friends_returned = list()
        pipeline = [{'$match': {'user_id': self.getUserId()}},
                    {'$lookup': {'from': 'users_info', 'localField': 'friend_id', 'foreignField': 'id',
                                 'as': 'users_info'}}]
        cursor = self.db[constants.COLLECTION_FRIENDS].aggregate(pipeline)
        friend_doc = yield cursor.to_list(None)
        if friend_doc:
            for friend in friend_doc:
                new_elem = dict()
                new_elem['user_id'] = friend['friend_id']
                user_info = friend['users_info'].pop()
                new_elem['first_name'] = user_info['first_name']
                new_elem['last_name'] = user_info['last_name']
                new_elem['sex'] = user_info['sex']
                friends_returned.append(new_elem)
            raise gen.Return(friends_returned)
        else:
            raise ApiError("Poczekaj szukamy przyjaciół.")

    @gen.coroutine
    def api_friends_add(self, user_info_id):
        friend_doc = yield self.db[constants.COLLECTION_FRIENDS].find_one(
            {constants.USER_ID: self.getUserId(),
             constants.FRIEND_ID: user_info_id})
        if not friend_doc:
            user_info_doc = yield self.api_user_info(user_info_id)
            if user_info_doc:
                result = dict()
                result[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]
                result[constants.FRIEND_ID] = str(user_info_id)
                friend_doc = yield self.db_insert(constants.COLLECTION_FRIENDS, result)

                if friend_doc:
                    raise gen.Return(user_info_id)
            raise ApiError('Nie udało się dodać użytkownika do przyjaciół.')
        else:
            raise ApiError('Użytkownik już jest dodany jako przyjaciel.')

    @gen.coroutine
    def api_friends_remove(self, user_info_id):

        pipeline = {constants.USER_ID: self.getUserId(),
                    constants.FRIEND_ID: user_info_id}

        friend_doc = yield self.db[constants.COLLECTION_FRIENDS].find_one(pipeline)
        if friend_doc:
            friend_doc = yield self.db_remove(constants.COLLECTION_FRIENDS, pipeline)
            if friend_doc:
                raise gen.Return(user_info_id)
        else:
            raise ApiError('Użytkownik nie jest przyjacielem.')

    @gen.coroutine
    def api_friends_suggestions(self):
        user_info = yield self.api_user_info()

        courses = dict()
        suggested_participants = dict()

        try:
            courses_editions_doc = yield self.api_courses_editions()

            if courses_editions_doc:
                for term in courses_editions_doc['course_editions']:
                    for course in courses_editions_doc['course_editions'][term]:
                        courses[course[constants.COURSE_ID]] = course

                for course in courses:
                    course_participants = yield self.api_course_edition(course, courses[course][constants.TERM_ID])
                    if not course_participants:
                        continue

                    cursor = self.db[constants.COLLECTION_FRIENDS].find()
                    friends_added = yield cursor.to_list(None)

                    for participant in course_participants[constants.PARTICIPANTS]:
                        participant_id = participant[constants.USER_ID]

                        # checking if participant is not current logged user
                        if user_info[constants.ID] == participant_id:
                            continue

                        # checking if participant is already added
                        poz = helpers.in_dictlist(constants.FRIEND_ID, participant_id, friends_added)
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

        except Exception as ex:
            yield self.exc(ex, finish=False)

        if not suggested_participants:
            raise ApiError("Poczekaj szukamy sugerowanych przyjaciół.")
        else:
            # sort by count descending and limit to 20 records
            suggested_participants = sorted(suggested_participants, key=lambda k: k['count'], reverse=True)

            raise gen.Return({
                'total': len(suggested_participants),
                'friends': suggested_participants
            })
