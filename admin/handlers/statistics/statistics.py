# coding=UTF-8

from tornado import web

from admin.handlers.base import BaseHandler
from commons import constants


class StatisticsBaseHandler(BaseHandler):
    async def _aggreate_users(self, pipeline):
        cursor = self.db[constants.COLLECTION_USERS].aggregate(pipeline)
        return await cursor.to_list(None)

    async def _stat_users_paired(self):
        pipeline = [{'$group': {"_id": {"user": "$user_id", "paired": "$usos_paired"}, "count": {'$sum': 1}}}]
        return await self._aggreate_users(pipeline)

    async def _stat_users_type(self):
        pipeline = [{'$group': {"_id": {"user": "$user_id", "user_type": "$user_type"}, "count": {'$sum': 1}
                                }
                     }
                    ]
        return await self._aggreate_users(pipeline)

    async def _stat_users_usos(self):
        pipeline = [{'$group': {"_id": {"user": "$user_id", "usos_id": "$usos_id"}, "count": {'$sum': 1}
                                }
                     }
                    ]
        return await self._aggreate_users(pipeline)

    @web.removeslash
    @web.asynchronous
    async def get(self):
        try:
            self._render_page("statistics/statistics.html")
        except Exception as ex:
            self._render_error(ex)
