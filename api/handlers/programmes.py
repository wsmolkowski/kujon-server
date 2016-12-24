# coding=UTF-8

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import config

LIMIT_FIELDS_PROGRAMMES = ('programme_id', 'description', 'name', 'mode_of_studies', 'level_of_studies', 'duration')


class ProgrammesByIdApi(ApiHandler):
    @decorators.authenticated
    async def get(self, programme_id):

        try:
            programme = await self.api_programme(programme_id, finish=False)
            if not programme:
                self.error("Brak podanego kierunku.", code=404)
            else:
                self.success(programme, cache_age=config.SECONDS_2MONTHS)
        except Exception as ex:
            await self.exc(ex)


class ProgrammesApi(ApiHandler):
    @decorators.authenticated
    async def get(self):

        try:
            programmes = await self.api_programmes()
            if not programmes:
                self.success(list())
            else:
                self.success(programmes, cache_age=config.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)
