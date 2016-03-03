import time
import logging

from tornado import gen
from tornado.ioloop import IOLoop

from commons import constants, settings
from commons.mongo_dao import Dao
from commons.usosutils.usoscrawler import UsosCrawler

if settings.DEBUG:
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt=settings.LOGGING_DATEFORMAT, level=logging.DEBUG)
    logging.debug("DEBUG MODE is ON")
else:
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt=settings.LOGGING_DATEFORMAT, level=logging.INFO)

SLEEP = 2


@gen.coroutine
def crawler():
    dao = Dao()
    crawler = UsosCrawler(dao=dao)

    initial_processing = list()

    @gen.coroutine
    def crawl_initial():

        for job_doc in dao.get_user_jobs(constants.JOB_START):
            if job_doc in initial_processing:
                return

            initial_processing.append(job_doc[constants.USER_ID])
            logging.info(u"starting initial_user_crawl for user {0}".format(job_doc[constants.USER_ID]))
            yield crawler.initial_user_crawl(job_doc[constants.USER_ID])

            dao.update_user_job(job_doc[constants.ID], constants.JOB_END)
            initial_processing.remove(job_doc[constants.USER_ID])
            logging.info(u"finished initial_user_crawl for user {0}".format(job_doc[constants.USER_ID]))

    @gen.coroutine
    def crawl_update():

        for job_doc in dao.get_user_jobs_for_update():
            if job_doc[constants.USER_ID] in initial_processing:
                return

            initial_processing.append(job_doc[constants.USER_ID])
            logging.info(u"creating update_user_crawl for user {0}".format(job_doc[constants.USER_ID]))

            dao.insert_user_job(job_doc[constants.USER_ID])

            initial_processing.remove(job_doc[constants.USER_ID])
            logging.info(u"finished update_user_crawl for user {0}".format(job_doc[constants.USER_ID]))

    @gen.coroutine
    def worker_initial():
        while True:
            yield [crawl_update(), crawl_initial()]
            time.sleep(SLEEP)

    worker_initial()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ioLoop = IOLoop.instance()
    ioLoop.add_callback(crawler)
    ioLoop.start()