import chronos

from tornado.log import enable_pretty_logging

from commons import utils
from commons.usosutils.usoscrawler import UsosCrawler
from commons.mongo_util import reindex, save_statistics


utils.initialize_logging('scheduler')


def update_time_table():
    uc = UsosCrawler()
    uc.update_time_tables()


def init():

    # bind a ioloop or use default ioloop
    chronos.setup()  # chronos.setup(tornado.ioloop.IOLoop())
    chronos.schedule('update_time_table', chronos.every_second(86400), update_time_table)   # 86400 => 1 day
    chronos.schedule('reindex', chronos.every_second(86400), reindex)   # 86400 => 1 day
    chronos.schedule('save_statistics', chronos.every_second(86400), save_statistics)   # 86400 => 1 day

    chronos.start(True)

if __name__ == '__main__':

    enable_pretty_logging()
    init()