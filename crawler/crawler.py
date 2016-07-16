# coding=UTF-8
# http://stackoverflow.com/questions/37068709/python-tornado-queue-toro-task-consuming-in-parallel

import logging
from datetime import datetime

import motor
from tornado import queues, gen
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line

from commons import settings, constants
from usoscrawler import UsosCrawler

QUEUE_MAXSIZE = 100
MAX_WORKERS = 4
SLEEP = 2


class MongoDbQueue(object):
    def __init__(self):

        self.queue = queues.Queue(maxsize=QUEUE_MAXSIZE)
        self.db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]
        self.processing = []

        logging.info(self.db)

    @gen.coroutine
    def load_work(self):

        # create jobs and put into queue
        cursor = self.db[constants.COLLECTION_JOBS_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (yield cursor.fetch_next):
            if len(self.processing) >= MAX_WORKERS:
                break
            job = cursor.next_object()
            logging.debug('putting job to queue for type: {0} queue size: {1}'.format(job[constants.JOB_TYPE],
                                                                                      self.queue.qsize()))
            yield self.queue.put(job)

        raise gen.Return()

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

        logging.info(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

        raise gen.Return()

    @gen.coroutine
    def process_job(self, job):
        try:
            self.processing.append(job)
            logging.info("processing job: {0} with job type: {1} queue size: {2}".format(
                job[constants.MONGO_ID], job[constants.JOB_TYPE], self.queue.qsize()))
            yield self.update_job(job, constants.JOB_START)

            if job[constants.JOB_TYPE] == 'initial_user_crawl':
                yield UsosCrawler().initial_user_crawl(job[constants.USER_ID])
            elif job[constants.JOB_TYPE] == 'archive_user':
                yield UsosCrawler().archive_user(job[constants.USER_ID])
            elif job[constants.JOB_TYPE] == 'subscribe_usos':
                yield UsosCrawler().subscribe(job[constants.USER_ID])
            elif job[constants.JOB_TYPE] == 'subscription_event':
                yield UsosCrawler().process_event(job[constants.JOB_DATA])
            else:
                raise Exception("could not process job with unknown job type: {0}".format(job[constants.JOB_TYPE]))
            yield self.update_job(job, constants.JOB_FINISH)

            logging.info(
                "processed job: {0} with job type: {1}".format(job[constants.MONGO_ID], job[constants.JOB_TYPE]))
        finally:
            self.processing.remove(job)

    @gen.coroutine
    def worker(self):
        while True:
            try:
                job = yield self.queue.get()
                logging.info("consuming queue job {0}. current queue size: {1} processing: {2}".format(
                    job, self.queue.qsize(), len(self.processing)))
                yield self.process_job(job)
            except Exception as ex:
                msg = "Exception while executing job {0} with: {1}".format(job[constants.MONGO_ID], ex)
                logging.exception(msg)
                yield self.update_job(job, constants.JOB_FAIL, msg)
            finally:
                self.queue.task_done()

    @gen.coroutine
    def producer(self):
        while True:
            yield self.load_work()
            yield gen.sleep(SLEEP)

    @gen.coroutine
    def workers(self):
        IOLoop.current().spawn_callback(self.producer)
        futures = [self.worker() for _ in range(MAX_WORKERS)]
        yield futures


if __name__ == '__main__':
    parse_command_line()

    logging.getLogger().setLevel(settings.LOG_LEVEL)

    mongoQueue = MongoDbQueue()

    io_loop = IOLoop.current()
    io_loop.run_sync(mongoQueue.workers)
