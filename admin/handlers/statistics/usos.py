# coding=UTF-8

from tornado import web

from admin.handlers.statistics.statistics import StatisticsBaseHandler


class UsosHandler(StatisticsBaseHandler):
    @web.removeslash
    @web.asynchronous
    async def get(self):
        try:
            usos_users = await self._stat_usos_users()
            usos_errors = await self._stat_usos_errors()
            self._render_page("statistics/usos.html", {
                'usos_users': usos_users,
                'usos_errors': usos_errors
            })
        except Exception as ex:
            self._render_error(ex)
