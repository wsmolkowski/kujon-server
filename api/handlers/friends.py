# coding=UTF-8

import tornado.web

from api.handlers.base import ApiHandler
from commons import constants, decorators


class FriendsApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self):
        try:
            friends = await self.api_friends()
            self.success(friends, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)

    @decorators.authenticated
    @tornado.web.asynchronous
    async def post(self, user_info_id):
        try:
            add = await self.api_friends_add(user_info_id)
            self.success(add)
            return
        except Exception as ex:
            await self.exc(ex)

    @decorators.authenticated
    @tornado.web.asynchronous
    async def delete(self, user_info_id):
        try:
            remove = await self.api_friends_remove(user_info_id)
            self.success(remove)
        except Exception as ex:
            await self.exc(ex)


class FriendsSuggestionsApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self):
        try:
            friends_suggestions = await self.api_friends_suggestions()
            if not friends_suggestions:
                self.error("Poczekaj szukamy sugerowanych przyjaciół.")
            else:
                self.success(friends_suggestions, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)
