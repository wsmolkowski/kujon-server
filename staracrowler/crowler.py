import time
import logging

from tornado import gen
from tornado.ioloop import IOLoop

from staracommon import constants
from staracommon.mongo_dao import Dao
from staracommon.usosutils.usoscrowler import UsosCrowler

SLEEP = 10


@gen.coroutine
def main():
    dao = Dao()
    usos_crowler = UsosCrowler(dao=dao)

    initial_processing = []

    @gen.coroutine
    def crowl_initial():

        for user_id in dao.get_initial_users():
            if user_id in initial_processing:
                return

            initial_processing.append(user_id)
            logging.info("starting initial_user_crowl for {0}".format(user_id[constants.USER_ID]))
            yield usos_crowler.initial_user_crowl(user_id[constants.USER_ID])
            logging.info("finished initial_user_crowl for {0}".format(user_id[constants.USER_ID]))

            initial_processing.remove(user_id)
            time.sleep(SLEEP)

    @gen.coroutine
    def worker_initial():
        while True:
            yield crowl_initial()

    worker_initial()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #IOLoop.current().start()
    IOLoop.current().run_sync(main)