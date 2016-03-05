import logging
from datetime import timedelta, datetime

import motor
from tornado import queues, gen, ioloop
from tornado.log import enable_pretty_logging

from commons import settings, constants
from commons.usosutils.usoscrawler import UsosCrawler
import job_factory

QUEUE_MAXSIZE = 100
SLEEP = 1


class MongoDbQueue(object):
    def __init__(self, queue_maxsize=QUEUE_MAXSIZE):
        super(MongoDbQueue, self).__init__()

        self.crawler = UsosCrawler()
        self._queue = queues.Queue(maxsize=queue_maxsize)

        self._db = self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]

    @gen.coroutine
    def __load_work(self):

        # check if data for users should be updated
        delta = datetime.now() - timedelta(minutes=constants.CRAWL_USER_UPDATE)

        cursor = self._db[constants.COLLECTION_JOBS_QUEUE].find(
            {constants.UPDATE_TIME: {'$gt': delta}, constants.JOB_STATUS: constants.JOB_FINISH}
        )

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            new_job = yield self._db[constants.COLLECTION_JOBS_QUEUE].insert(
                job_factory.update_user_job(job[constants.USER_ID]))
            logging.debug('created new job with type: {0}'.format(new_job))

        # create jobs and put into queue
        cursor = self._db[constants.COLLECTION_JOBS_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            logging.debug('putting job to queue for user: {0} and type: {1}'.format(job[constants.USER_ID],
                                                                                    job[constants.JOB_TYPE]))
            yield self._queue.put(job)

    @gen.coroutine
    def update_job(self, job, status, message=None):
        job[constants.JOB_STATUS] = status
        job[constants.UPDATE_TIME] = datetime.now()
        if message:
            job[constants.JOB_MESSAGE] = message
        update = yield self._db[constants.COLLECTION_JOBS_QUEUE].update({constants.ID: job[constants.ID]}, job)

        logging.debug('updated job: {0} with status: {1} resulted in: {2}'.format(job[constants.ID], status, update))

    @gen.coroutine
    def process_job(self, job):
        logging.debug('processing job: {0} with job type: {1}'.format(job[constants.ID], job[constants.JOB_TYPE]))

        if job[constants.JOB_TYPE] == 'initial_user_crawl':
            yield self.crawler.initial_user_crawl(job[constants.USER_ID])
        elif job[constants.JOB_TYPE] == 'update_user_crawl':
            yield self.crawler.initial_user_crawl(job[constants.USER_ID])  # FIXME - create dedicated method
        else:
            raise Exception('could not process job with unknown job type: {0}'.format(job[constants.JOB_TYPE]))

        logging.debug('processed job: {0} with job type: {1}'.format(job[constants.ID], job[constants.JOB_TYPE]))

    @gen.coroutine
    def worker(self):

        while True:

            if self._queue.empty():
                yield gen.sleep(SLEEP)
                yield self.__load_work()

            else:
                job = yield self._queue.get()
                logging.debug('consuming queue job {0}'.format(job))

                try:
                    yield self.update_job(job, constants.JOB_START)

                    yield self.process_job(job)

                    yield self.update_job(job, constants.JOB_FINISH)

                except Exception, ex:
                    msg = 'Exception while executing job {0} {1}', job[constants.ID]
                    logging.exception("{0} {1}".format(msg, ex.message))

                    yield self.update_job(job, constants.JOB_FAIL, msg)
                finally:
                    self._queue.task_done()


if __name__ == '__main__':
    enable_pretty_logging()
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("DEBUG MODE is ON")

    mq = MongoDbQueue()

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(mq.worker)
