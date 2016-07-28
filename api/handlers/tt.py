# coding=UTF-8

import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class TTApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self, given_date):

        try:
            tt_doc = await self.api_tt(given_date)
            self.success(tt_doc, cache_age=constants.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)
