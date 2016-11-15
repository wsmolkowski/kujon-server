# coding=UTF-8

from bson import SON
from tornado import web

from admin.handlers.statistics.statistics import StatisticsBaseHandler


class DatabaseHandler(StatisticsBaseHandler):
    def _convert_bytes(self, bytes):
        bytes = float(bytes)
        magnitude = abs(bytes)
        if magnitude >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fT' % terabytes
        elif magnitude >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fG' % gigabytes
        elif magnitude >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fM' % megabytes
        elif magnitude >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fK' % kilobytes
        else:
            size = '%.2fb' % bytes
        return size

    async def _database_statistics(self):

        result = []

        collection_names = await self.db.collection_names(include_system_collections=False)
        for collection_name in collection_names:
            collstats = await self.db.command(SON([("collstats", collection_name)]))

            result.append({
                'collection_name': collection_name,
                'count': collstats['count'],
                'size': self._convert_bytes(collstats['size']),
                'totalIndexSize': self._convert_bytes(collstats['totalIndexSize'])
            })

        return result

    @web.removeslash
    @web.asynchronous
    async def get(self):
        try:
            database_statistics = await self._database_statistics()

            database_statistics = sorted(database_statistics, key=lambda k: k['collection_name'])

            self._render_page("statistics/database.html", {
                'database_statistics': database_statistics,
            })

        except Exception as ex:
            self._render_error(ex)
