# coding=UTF-8

import tornado.gen
import tornado.web

from api.handlers.base import ApiHandler
from commons import constants, decorators


class FriendsApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            friends = yield self.api_friends()
            self.success(friends, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            yield self.exc(ex)

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, user_info_id):
        try:
            add = yield self.api_friends_add(user_info_id)
            self.success(add)
            return
        except Exception as ex:
            yield self.exc(ex)

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self, user_info_id):
        try:
            remove = yield self.api_friends_remove(user_info_id)
            self.success(remove)
        except Exception as ex:
            yield self.exc(ex)


class FriendsSuggestionsApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            frendssuggestions = yield self.api_friendssuggestions()
            if not frendssuggestions:
                self.error("Poczekaj szukamy sugerowanych przyjaciół.")
            else:
                self.success(frendssuggestions, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            yield self.exc(ex)
