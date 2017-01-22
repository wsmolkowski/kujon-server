# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import config


class TermsApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self):

        try:
            terms_ordered = await self.api_terms()
            if not terms_ordered:
                self.error("Nie znaleziono cykli.")
            else:
                self.success(terms_ordered, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)


class TermApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self, term_id):

        try:
            term_doc = await self.api_term([term_id])

            if not term_doc:
                self.error("Nie znaleźliśmy danego semestru.", code=404)
            else:
                self.success(term_doc, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)
