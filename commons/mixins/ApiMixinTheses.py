# coding=UTF-8

from tornado import gen

from commons import constants
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin


class ApiMixinTheses(DaoMixin, UsosMixin):

    @gen.coroutine
    def api_theses(self):

        users_info_doc = yield self.api_user_info()
        theses_doc = yield self.usos_theses(users_info_doc[constants.ID])
        raise gen.Return(theses_doc)

