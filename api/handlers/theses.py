# coding=UTF-8

from api.handlers.base.api import ApiHandler
from commons import decorators
from commons.constants import config


class ThesesApi(ApiHandler):
    @decorators.authenticated
    async def get(self):
        try:
            theses_doc = await self.api_thesis()
            self.success(theses_doc, cache_age=config.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex, finish=True)
