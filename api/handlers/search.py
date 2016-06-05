# coding=UTF-8

import tornado.gen
import tornado.web
from base import ApiHandler
from commons import decorators


class SearchUsersApi(ApiHandler):

    def __validate_query_input(self, query):
        if len(query) < 3 or len(query) > 30:
            self.error("Niepoprawne zapytnie. Spróbuj wyszukać fragment dłuższy niż 3 znaki i krótszy niż 30.")
            return False
        return True

    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, query):
        try:

            if not self.__validate_query_input(query):
                return

            add = yield self.api_search_user(query)
            self.success(add)
            return
        except Exception, ex:
            yield self.exc(ex)

