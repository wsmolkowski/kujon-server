# coding=UTF-8

from tornado import gen

from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin


class ApiMixinSearch(DaoMixin, UsosMixin):

    @gen.coroutine
    def api_search_users(self, query):
        start = self.get_argument('start', default=0, strip=True)
        self._search_options = (query, 'users')
        search_doc = yield self.usos_search_users(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_courses(self, query):
        start = self.get_argument('start', default=0, strip=True)
        search_doc = yield self.usos_search_courses(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_faculties(self, query):
        start = self.get_argument('start', default=0, strip=True)
        search_doc = yield self.usos_search_faculty(query, start)
        raise gen.Return(search_doc)

    @gen.coroutine
    def api_search_programmes(self, query):
        start = self.get_argument('start', default=0, strip=True)
        search_doc = yield self.usos_search_programmes(query, start)
        raise gen.Return(search_doc)
