# coding=UTF-8

from bson.objectid import ObjectId
from tornado import gen

from commons import constants, helpers
from commons.errors import ApiError, UsosClientError
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin


class ApiMixinSearch(DaoMixin, UsosMixin):

    @gen.coroutine
    def _save_query(self, query):
        # TODO save query in mongo
        pass

    @staticmethod
    def validate_query_input(query):
        if len(query) < 3 or len(query) > 30:
            raise ApiError("Niepoprawne zapytnie. Spróbuj wyszukać fragment dłuższy niż 3 znaki i krótszy niż 30.")
        return True

    @gen.coroutine
    def api_search_user(self, query):

        start = self.get_argument('start', default=0, strip=True)

        self.validate_query_input(query)
        yield self._save_query(query)
        search_doc = yield self.usos_search_users(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_course(self, query):

        start = self.get_argument('start', default=0, strip=True)
        yield self._save_query(query)
        search_doc = yield self.usos_search_courses(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_faculty(self, query):
        start = self.get_argument('start', default=0, strip=True)
        yield self._save_query(query)
        search_doc = yield self.usos_search_faculty(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_programmes(self, query):
        start = self.get_argument('start', default=0, strip=True)
        yield self._save_query(query)
        search_doc = yield self.usos_search_programmes(query, start)
        raise gen.Return(search_doc)
