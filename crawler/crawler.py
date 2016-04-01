# coding=UTF-8

import logging
from datetime import timedelta, datetime

import motor
from tornado import queues, gen, ioloop
from tornado.options import parse_command_line

from commons import settings, constants
from commons.mixins.DatabaseMixin import DatabaseMixin
from commons.usosutils.usoscrawler import UsosCrawler

QUEUE_MAXSIZE = 100
SLEEP = 1


class MongoDbQueue(DatabaseMixin):
    def __init__(self, queue_maxsize=QUEUE_MAXSIZE):
        super(MongoDbQueue, self).__init__()

        self.crawler = UsosCrawler()
        self._queue = queues.Queue(maxsize=queue_maxsize)

    @gen.coroutine
    def __load_work(self):

        # check if data for users should be updated
        delta = datetime.now() - timedelta(minutes=constants.CRAWL_USER_UPDATE)

        cursor = self.db[constants.COLLECTION_JOBS_QUEUE].find(
            {constants.UPDATE_TIME: {'$lt': delta}, constants.JOB_STATUS: constants.JOB_FINISH}
        ).sort([(constants.UPDATE_TIME, -1)])

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            yield self.update_job(job, constants.JOB_PENDING)

        # create jobs and put into queue
        cursor = self.db[constants.COLLECTION_JOBS_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            logging.debug('putting job to queue for user: {0} and type: {1}'.format(job[constants.USER_ID],
                                                                                    job[constants.JOB_TYPE]))
            yield self._queue.put(job)

    @gen.coroutine
    def update_job(self, job, status, message=None):
        # insert current job to history collection
        old = job.copy()
        old.pop(constants.MONGO_ID)
        yield self.db[constants.COLLECTION_JOBS_LOG].insert(old)

        # change values and update
        job[constants.JOB_STATUS] = status
        job[constants.UPDATE_TIME] = datetime.now()
        job[constants.JOB_MESSAGE] = message

        update = yield self.db[constants.COLLECTION_JOBS_QUEUE].update(
                {constants.MONGO_ID: job[constants.MONGO_ID]}, job)

        logging.debug("updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    @gen.coroutine
    def process_job(self, job):
        logging.debug("processing job: {0} with job type: {1}".format(job[constants.MONGO_ID], job[constants.JOB_TYPE]))

        if job[constants.JOB_TYPE] == 'initial_user_crawl':
            yield self.crawler.initial_user_crawl(job[constants.USER_ID])
        elif job[constants.JOB_TYPE] == 'update_user_crawl':
            yield self.crawler.update_user_crawl(job[constants.USER_ID])
        elif job[constants.JOB_TYPE] == 'remove_user':
            yield self.remove_user_data(job[constants.USER_ID])
        else:
            raise Exception("could not process job with unknown job type: {0}".format(job[constants.JOB_TYPE]))

        logging.debug("processed job: {0} with job type: {1}".format(job[constants.MONGO_ID], job[constants.JOB_TYPE]))

    @gen.coroutine
    def worker(self):

        while True:

            if self._queue.empty():
                yield gen.sleep(SLEEP)
                yield self.__load_work()

            else:
                job = yield self._queue.get()
                logging.debug("consuming queue job {0}".format(job))

                try:
                    yield self.update_job(job, constants.JOB_START)

                    yield self.process_job(job)

                    yield self.update_job(job, constants.JOB_FINISH)

                except Exception, ex:
                    msg = "Exception while executing job {0} with: {1}".format(job[constants.MONGO_ID], ex.message)
                    logging.exception(msg)

                    yield self.update_job(job, constants.JOB_FAIL, msg)
                finally:
                    self._queue.task_done()


if __name__ == '__main__':
    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    mq = MongoDbQueue()

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(mq.worker)
