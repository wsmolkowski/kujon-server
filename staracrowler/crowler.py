import time
import logging

from tornado import gen
from tornado.ioloop import IOLoop

from staracommon import constants
from staracommon.mongo_dao import Dao
from staracommon.usosutils.usoscrowler import UsosCrowler

SLEEP = 2


@gen.coroutine
def crowl():
    dao = Dao()
    usos_crowler = UsosCrowler(dao=dao)

    initial_processing = []

    @gen.coroutine
    def crowl_initial():

        for job_doc in dao.get_user_jobs(constants.JOB_START):
            if job_doc in initial_processing:
                return

            initial_processing.append(job_doc)
            logging.info("starting initial_user_crowl for user {0}".format(job_doc[constants.USER_ID]))
            yield usos_crowler.initial_user_crowl(job_doc[constants.USER_ID])

            dao.update_user_job(job_doc[constants.ID], constants.JOB_END)
            initial_processing.remove(job_doc)
            logging.info("finished initial_user_crowl for user {0}".format(job_doc[constants.USER_ID]))

    @gen.coroutine
    def worker_initial():
        while True:
            yield crowl_initial()
            time.sleep(SLEEP)

    worker_initial()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ioLoop = IOLoop.instance()
    ioLoop.add_callback(crowl)
    ioLoop.start()