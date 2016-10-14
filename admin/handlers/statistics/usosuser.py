# coding=UTF-8

from tornado import web

from admin.handlers.statistics.statistics import StatisticsBaseHandler


class UsosUserHandler(StatisticsBaseHandler):
    @web.removeslash
    @web.asynchronous
    async def get(self):
        try:
            usos_users_paired = await self._stat_usos_users_paired()
            self._render_page("statistics/usosuser.html", {
                'usos_users_paired': usos_users_paired,
            })
        except Exception as ex:
            self._render_error(ex)
