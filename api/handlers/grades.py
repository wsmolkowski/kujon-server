# coding=UTF-8

import tornado.web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class GradesForUserApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self):
        try:
            grades_doc = await self.api_grades()
            self.success(grades_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)


class GradesForUserByTermApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self):
        try:
            grades_doc = await self.api_grades_byterm()
            self.success(grades_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)
