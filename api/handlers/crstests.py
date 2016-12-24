# coding=UTF-8

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import config
from commons.mixins.CrsTestsMixin import CrsTestsMixin


class CrsTestsApi(ApiHandler, CrsTestsMixin):
    @decorators.authenticated
    async def get(self):

        try:
            crstests_doc = await self.api_crstests()
            if not crstests_doc:
                self.error("Brak inforamcji o Twoich sprawdzianach.", code=404)
            else:
                self.success(crstests_doc, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)


class CrsTestsNodeApi(ApiHandler, CrsTestsMixin):
    @decorators.authenticated
    async def get(self, node_id):

        try:
            crstest_node_doc = await self.api_crstests_grades(node_id)

            if not crstest_node_doc:
                self.error("Brak informacji o danym sprawdzianie.", code=404)
            else:
                self.success(crstest_node_doc, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)
