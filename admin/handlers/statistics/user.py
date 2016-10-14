# coding=UTF-8

from tornado import web

from admin.handlers.statistics.statistics import StatisticsBaseHandler


class UsersHandler(StatisticsBaseHandler):
    @web.removeslash
    @web.asynchronous
    async def get(self):
        try:
            users_paired = await self._stat_users_paired()
            users_type = await self._stat_users_type()
            users_usos = await self._stat_users_usos()

            self._render_page("statistics/user.html", {
                'users_paired': users_paired,
                'users_type': users_type,
                'users_usos': users_usos
            })
        except Exception as ex:
            self._render_error(ex)
