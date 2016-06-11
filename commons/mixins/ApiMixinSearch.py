# coding=UTF-8

from tornado import gen

from commons.errors import ApiError
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin
from datetime import datetime
from commons import constants


class ApiMixinSearch(DaoMixin, UsosMixin):

    @gen.coroutine
    def _save_query(self, query, endpoint):
        query_doc = dict()
        query_doc[constants.CREATED_TIME] = datetime.now()
        query_doc[constants.USER_ID] = self.user_doc[constants.MONGO_ID]
        query_doc[constants.SEARCH_QUERY] = query
        query_doc[constants.SEARCH_ENDPOINT] = endpoint
        query_doc = yield self.db_insert(constants.COLLECTION_SEARCH, query_doc)
        raise gen.Return(query_doc)

    @staticmethod
    def validate_query_input(query):
        if len(query) < 3 or len(query) > 30:
            raise ApiError("Niepoprawne zapytnie. Spróbuj wyszukać fragment dłuższy niż 3 znaki i krótszy niż 30.")
        return True

    @gen.coroutine
    def api_search_users(self, query):

        start = self.get_argument("start", default=0, strip=True)

        self.validate_query_input(query)
        yield self._save_query(query, "users")
        search_doc = yield self.usos_search_users(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_courses(self, query):

        start = self.get_argument("start", default=0, strip=True)
        yield self._save_query(query, "courses")
        search_doc = yield self.usos_search_courses(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_faculties(self, query):
        start = self.get_argument("start", default=0, strip=True)
        yield self._save_query(query, "faculties")
        search_doc = yield self.usos_search_faculty(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_programmes(self, query):
        start = self.get_argument("start", default=0, strip=True)
        yield self._save_query(query, "programmes")
        search_doc = yield self.usos_search_programmes(query, start)
        raise gen.Return(search_doc)
