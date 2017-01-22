# coding=UTF-8

from api.handlers.base.api import ApiHandler
from commons import decorators
from commons.constants import config


class GradesForUserApi(ApiHandler):
    @decorators.authenticated
    async def get(self):
        try:
            grades_doc = await self.api_grades()
            self.success(grades_doc, cache_age=config.SECONDS_DAY)
        except Exception as ex:
            await self.exc(ex)


class GradesForUserByTermApi(ApiHandler):
    @decorators.authenticated
    async def get(self):
        try:
            grades_doc = await self.api_grades_byterm()
            self.success(grades_doc, cache_age=config.SECONDS_DAY)
        except Exception as ex:
            await self.exc(ex)
