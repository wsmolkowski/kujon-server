# coding=UTF-8

from api.handlers.base import ApiHandler
from commons import decorators, helpers
from commons.constants import config, collections, fields
from commons.errors import ApiError


class AbstractFriendHandler(ApiHandler):

    async def api_friends(self):
        friends_returned = list()
        pipeline = [{'$match': {'user_id': self.getUserId()}},
                    {'$lookup': {'from': 'users_info', 'localField': 'friend_id', 'foreignField': 'id',
                                 'as': 'users_info'}}]
        cursor = self.db[collections.FRIENDS].aggregate(pipeline)
        friend_doc = await cursor.to_list(None)
        if friend_doc:
            for friend in friend_doc:
                new_elem = dict()
                new_elem['user_id'] = friend['friend_id']
                user_info = friend['users_info'].pop()
                new_elem['first_name'] = user_info['first_name']
                new_elem['last_name'] = user_info['last_name']
                new_elem['sex'] = user_info['sex']
                friends_returned.append(new_elem)

            return friends_returned
        else:
            return friend_doc

    async def api_friends_add(self, user_info_id):
        friend_doc = await self.db[collections.FRIENDS].find_one(
            {fields.USER_ID: self.getUserId(),
             fields.FRIEND_ID: user_info_id})
        if not friend_doc:
            user_info_doc = await self.api_user_info(user_info_id)
            if user_info_doc:
                result = dict()
                result[fields.USER_ID] = self.get_current_user()[fields.MONGO_ID]
                result[fields.FRIEND_ID] = str(user_info_id)
                friend_doc = await self.db_insert(collections.FRIENDS, result)

                if friend_doc:
                    return user_info_id
            raise ApiError('Nie udało się dodać użytkownika do przyjaciół.')
        else:
            raise ApiError('Użytkownik już jest dodany jako przyjaciel.')

    async def api_friends_remove(self, user_info_id):

        pipeline = {fields.USER_ID: self.getUserId(),
                    fields.FRIEND_ID: user_info_id}

        friend_doc = await self.db[collections.FRIENDS].find_one(pipeline)
        if friend_doc:
            friend_doc = await self.db_remove(collections.FRIENDS, pipeline)
            if friend_doc:
                return user_info_id
        else:
            raise ApiError('Użytkownik nie jest przyjacielem.')

    async def api_friends_suggestions(self):
        user_info = await self.api_user_usos_info()

        courses = dict()
        suggested_participants = dict()

        try:
            if not user_info:
                raise CallerError("Wystąpił problem z dostępem do usług USOS API. Spróbuj ponownie za chwilę.")

            courses_editions_doc = await self.api_courses_editions()
            if not courses_editions_doc:
                raise ApiError("Poczekaj szukamy znajomych w Twoim otoczeniu.")

            if courses_editions_doc:
                for term in courses_editions_doc['course_editions']:
                    for course in courses_editions_doc['course_editions'][term]:
                        courses[course[fields.COURSE_ID]] = course

                for course in courses:
                    course_participants = await self.api_course_edition(course, courses[course][fields.TERM_ID])
                    if not course_participants:
                        continue

                    cursor = self.db[collections.FRIENDS].find()
                    friends_added = await cursor.to_list(None)

                    for participant in course_participants[fields.PARTICIPANTS]:
                        participant_id = participant[fields.USER_ID]

                        # checking if participant is not current logged user
                        if user_info[fields.ID] == participant_id:
                            continue

                        # checking if participant is already added
                        poz = helpers.in_dictlist(fields.FRIEND_ID, participant_id, friends_added)
                        if poz:
                            continue
                        del participant[fields.ID]

                        # count how many courses have together
                        if participant_id in suggested_participants:
                            suggested_participants[participant_id]['count'] += 1
                        else:
                            suggested_participants[participant_id] = participant
                            suggested_participants[participant_id]['count'] = 1

                suggested_participants = suggested_participants.values()

        except Exception as ex:
            await self.exc(ex, finish=False)

        if not suggested_participants:
            raise ApiError("Poczekaj szukamy sugerowanych przyjaciół.")
        else:
            # sort by count descending and limit to 20 records
            suggested_participants = sorted(suggested_participants, key=lambda k: k['count'], reverse=True)

            return {'total': len(suggested_participants), 'friends': suggested_participants}


class FriendsApi(AbstractFriendHandler):
    @decorators.authenticated
    async def get(self):
        try:
            friends = await self.api_friends()
            self.success(friends, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)

    @decorators.authenticated
    async def post(self, user_info_id):
        try:
            add = await self.api_friends_add(user_info_id)
            self.success(add)
            return
        except Exception as ex:
            await self.exc(ex)

    @decorators.authenticated
    async def delete(self, user_info_id):
        try:
            remove = await self.api_friends_remove(user_info_id)
            self.success(remove)
        except Exception as ex:
            await self.exc(ex)


class FriendsSuggestionsApi(AbstractFriendHandler):
    @decorators.authenticated
    async def get(self):
        try:
            friends_suggestions = await self.api_friends_suggestions()
            if not friends_suggestions:
                self.error("Poczekaj szukamy sugerowanych przyjaciół.")
            else:
                self.success(friends_suggestions, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)
