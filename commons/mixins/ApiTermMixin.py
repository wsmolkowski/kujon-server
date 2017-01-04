# coding=UTF-8

import logging
from datetime import date, datetime

from pymongo.errors import DuplicateKeyError
from tornado import gen

from commons.constants import collections, fields
from commons.errors import ApiError

TERM_LIMIT_FIELDS = {'name': 1, 'end_date': 1, 'finish_date': 1, 'start_date': 1, fields.TERM_ID: 1,
                     fields.TERMS_ORDER_KEY: 1, fields.MONGO_ID: 0}


class ApiTermMixin(object):
    async def _api_term_task(self, term_id):
        term_doc = None
        try:
            term_doc = await self.asyncCall(
                path='services/terms/term', arguments={'term_id': term_id}
            )
            term_doc[fields.TERM_ID] = term_doc.pop(fields.ID)

            await self.db_insert(collections.TERMS, term_doc)
        except DuplicateKeyError as ex:
            logging.debug(ex)
        except Exception as ex:
            await self.exc(ex, finish=False)
        finally:
            return term_doc

    async def api_term(self, term_ids):

        pipeline = {fields.TERM_ID: {"$in": term_ids}, fields.USOS_ID: self.getUsosId()}
        if self.do_refresh():
            await self.db_remove(collections.TERMS, pipeline)

        cursor = self.db[collections.TERMS].find(pipeline, TERM_LIMIT_FIELDS).sort(
            fields.TERMS_ORDER_KEY, -1)
        terms_doc = await cursor.to_list(None)

        if not terms_doc:
            try:
                terms_task = list()
                for term_id in term_ids:
                    terms_task.append(self._api_term_task(term_id))
                await gen.multi(terms_task)

                cursor = self.db[collections.TERMS].find(pipeline, TERM_LIMIT_FIELDS).sort(
                    fields.TERMS_ORDER_KEY, -1)
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

        return terms_doc

    async def api_terms(self):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy jednostek.")

        terms_ids = list()
        for term_id in courses_editions[fields.COURSE_EDITIONS]:
            if term_id not in terms_ids:
                terms_ids.append(term_id)

        return await self.api_term(terms_ids)
