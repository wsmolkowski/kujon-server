# coding=UTF-8

from bson.objectid import ObjectId
from tornado import gen

from commons import constants, helpers
from commons.errors import ApiError, UsosClientError
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin


class ApiMixinSearch(DaoMixin, UsosMixin):

    @gen.coroutine
    def api_search_user(self, query):

        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        search_doc = yield self.usos_search_users(query, usos_doc)

        raise gen.Return(search_doc)

