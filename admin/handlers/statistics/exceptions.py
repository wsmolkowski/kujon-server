# coding=UTF-8

from datetime import datetime, timedelta

from tornado import web

from admin.handlers.statistics.statistics import StatisticsBaseHandler
from commons.constants import fields, collections


class ExceptionsHandler(StatisticsBaseHandler):
    async def _stat_daily_exceptions(self):
        yesterday = datetime.now() - timedelta(days=1)

        pipeline = [
            {"$match": {fields.CREATED_TIME: {"$gt": yesterday}}},
            {
                "$group": {
                    "_id": {
                        "exception_type": {"$ifNull": ["$exception_type", "Unknown"]},
                        "message": {"$ifNull": ["$message", "Unknown"]},
                        "exception": {"$ifNull": ["$exception", "Unknown"]},
                        "usos_id": {"$ifNull": ["$usos_id", "Unknown"]}
                    },
                    "count": {"$sum": 1}
                }
            }]
        cursor = self.db[collections.COLLECTION_EXCEPTIONS].aggregate(pipeline)
        return await cursor.to_list(None)

    async def _stat_usos_errors(self):
        pipeline = [
            # {'$match': {'$usos_id': {'$exists': True, '$ne': None}}},
            {'$group': {'_id': {'usos_id': {'$ifNull': ["$usos_id", "Unknown"]}}, 'count': {'$sum': 1}}}
        ]
        cursor = self.db[fields.COLLECTION_EXCEPTIONS].aggregate(pipeline)
        return await cursor.to_list(None)

    @web.removeslash
    @web.asynchronous
    async def get(self):
        try:
            usos_errors, daily_exceptions = await self._stat_usos_errors(), await self._stat_daily_exceptions()

            self._render_page("statistics/exceptions.html", {
                'usos_errors': usos_errors,
                'daily_exceptions': daily_exceptions
            })

        except Exception as ex:
            self._render_error(ex)
