# coding=UTF-8

import asyncio
import logging

import aiohttp
import motor.motor_asyncio
from tornado.options import parse_command_line, define, options

from commons import constants
from commons.config import Config

define('environment', default='development')

SLEEP = 2


class UsosChecker(object):
    def __init__(self, config):
        self.config = config
        self.db = motor.motor_asyncio.AsyncIOMotorClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]

        if self.config.PROXY_PORT and self.config.PROXY_URL:
            proxy = 'http://{0}:{1}'.format(self.config.PROXY_URL, self.config.PROXY_PORT)
            self.conector = aiohttp.ProxyConnector(proxy=proxy, conn_timeout=50, limit=100)
        else:
            self.conector = aiohttp.TCPConnector(verify_ssl=False, limit=100)

    async def forever_check(self):
        session = aiohttp.ClientSession(connector=self.conector)

        while True:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
            async for usos_doc in cursor:
                url = usos_doc[
                          constants.USOS_URL] + 'services/events/notifier_status'  # 'services/courses/classtypes_index'
                try:
                    async with session.get(url) as response:
                        if response.status != 200 and 'application/json' not in response.headers['Content-Type']:
                            logging.info(url)
                            logging.error(response)
                        else:
                            json = await response.json()
                            logging.debug('USOS {0} response ok: {1}'.format(usos_doc[constants.USOS_ID], json))
                except Exception as ex:
                    logging.info(url)
                    logging.exception(ex)

            await asyncio.sleep(SLEEP)


def main():
    parse_command_line()

    config = Config(options.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)

    loop = asyncio.get_event_loop()
    checker = UsosChecker(config)
    loop.run_until_complete(checker.forever_check())


if __name__ == '__main__':
    main()
