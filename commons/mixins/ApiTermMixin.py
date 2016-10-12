# coding=UTF-8

import logging
from datetime import date, datetime

from pymongo.errors import DuplicateKeyError
from tornado import gen

from commons import constants
from commons.UsosCaller import AsyncCaller
from commons.errors import ApiError

LIMIT_FIELDS_TERMS = ('name', 'start_date', 'end_date', 'finish_date')
TERM_LIMIT_FIELDS = ('name', 'end_date', 'finish_date', 'start_date', 'term_id', constants.TERMS_ORDER_KEY)


class ApiTermMixin(object):
    async def _api_term_task(self, term_id):
        term_doc = None
        try:
            term_doc = await AsyncCaller(self._context).call_async(
                path='services/terms/term', arguments={'term_id': term_id}
            )
            # term_doc['name'] = term_doc['name']['pl']
            term_doc[constants.TERM_ID] = term_doc.pop(constants.ID)

            await self.db_insert(constants.COLLECTION_TERMS, term_doc)
        except DuplicateKeyError as ex:
            logging.debug(ex)
        except Exception as ex:
            await self.exc(ex, finish=False)
        finally:
            return term_doc

    async def api_term(self, term_ids):

        pipeline = {constants.TERM_ID: {"$in": term_ids}, constants.USOS_ID: self.getUsosId()}
        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_TERMS, pipeline)

        cursor = self.db[constants.COLLECTION_TERMS].find(pipeline, TERM_LIMIT_FIELDS).sort(
            constants.TERMS_ORDER_KEY, -1)
        terms_doc = await cursor.to_list(None)

        if not terms_doc:
            try:
                terms_task = list()
                for term_id in term_ids:
                    terms_task.append(self._api_term_task(term_id))
                await gen.multi(terms_task)

                cursor = self.db[constants.COLLECTION_TERMS].find(pipeline, TERM_LIMIT_FIELDS).sort(
                    constants.TERMS_ORDER_KEY, -1)
                terms_doc = await cursor.to_list(None)
            except Exception as ex:
                await self.exc(ex, finish=False)
                return

        today = date.today()
        for term in terms_doc:
            end_date = datetime.strptime(term['finish_date'], "%Y-%m-%d").date()
            if today <= end_date:
                term['active'] = True
            else:
                term['active'] = False
            del (term[constants.MONGO_ID])

        return terms_doc

    async def api_terms(self):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy jednostek.")

        terms_ids = list()
        for term_id in courses_editions[constants.COURSE_EDITIONS]:
            if term_id in terms_ids:
                continue
            terms_ids.append(term_id)

        result = await self.api_term(terms_ids)

        return result
