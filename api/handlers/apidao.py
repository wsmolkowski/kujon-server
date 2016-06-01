# coding=UTF-8

from commons import constants
from commons.mixins.ApiMixin import ApiMixin
from database import DatabaseHandler


class ApiDaoHandler(DatabaseHandler, ApiMixin):
    def do_refresh(self):  # overwrite from ApiMixin
        if self.request.headers.get(constants.MOBILE_X_HEADER_REFRESH, False):
            return True
        return False
