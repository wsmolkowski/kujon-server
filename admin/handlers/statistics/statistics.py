# coding=UTF-8

from tornado import web

from admin.handlers.base import BaseHandler
from commons import constants


class StatisticsBaseHandler(BaseHandler):
    async def _aggreate_users(self, pipeline):
        cursor = self.db[constants.COLLECTION_USERS].aggregate(pipeline)
        return await cursor.to_list(None)

    async def _stat_users_paired(self):
        pipeline = [
            {'$group': {'_id': {'user': '$user_id',
                                'paired': {'$ifNull': ["$usos_paired", "Unknown"]}
                                }, 'count': {'$sum': 1}}}
        ]
        return await self._aggreate_users(pipeline)

    async def _stat_users_type(self):
        pipeline = [
            {'$group': {'_id': {'user': '$user_id', 'user_type': '$user_type'}, 'count': {'$sum': 1}}}
        ]
        return await self._aggreate_users(pipeline)

    async def _stat_users_usos(self):
        pipeline = [
            {'$group': {'_id': {'user': '$user_id', 'usos_id': {'$ifNull': ["$usos_id", "Unknown"]}}, 'count': {'$sum': 1}}}
        ]
        return await self._aggreate_users(pipeline)

    async def _stat_usos_users(self):
        pipeline = [
            {'$match': {constants.USOS_PAIRED: True
                        }},
            {'$group': {'_id': {'user': '$user_id', 'usos_id': {'$ifNull': ["$usos_id", "Unknown"]}},
                        'count': {'$sum': 1}
                        }
             }]

        return await self._aggreate_users(pipeline)

    async def _stat_usos_users_paired(self):
        pipeline = [{
            '$group': {'_id': {'usos_id': {'$ifNull': ["$usos_id", "Unknown"]},
                               'paired': {'$ifNull': ["$usos_paired", "Unknown"]}
                               }, 'count': {'$sum': 1}}
        }, {'$sort': {'_id': 1}
            }]

        return await self._aggreate_users(pipeline)

    async def _stat_usos_errors(self):
        pipeline = [
            # {'$match': {'$usos_id': {'$exists': True, '$ne': None}}},
            {'$group': {'_id': {'usos_id': {'$ifNull': ["$usos_id", "Unknown"]}}, 'count': {'$sum': 1}}}
        ]
        cursor = self.db[constants.COLLECTION_EXCEPTIONS].aggregate(pipeline)
        return await cursor.to_list(None)

    @web.removeslash
    @web.asynchronous
    async def get(self):
        try:
            self._render_page('statistics/statistics.html')
        except Exception as ex:
            self._render_error(ex)
