import logging

from tornado.options import parse_command_line

import chronos
from commons import settings
from commons.mongo_util import reindex, save_statistics
from commons.usosutils.usoscrawler import UsosCrawler


def update_daily():
    uc = UsosCrawler()
    uc.daily_crawl()

def init():

    # bind a ioloop or use default ioloop
    chronos.setup()  # chronos.setup(tornado.ioloop.IOLoop())
    chronos.schedule('update_daily', chronos.every_second(604800), update_daily)   # 604800 => 7 days
    chronos.schedule('reindex', chronos.every_second(86400), reindex)   # 86400 => 1 day
    chronos.schedule('save_statistics', chronos.every_second(86400), save_statistics)   # 86400 => 1 day

    chronos.start(True)

if __name__ == '__main__':

    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    update_daily()
    # init()