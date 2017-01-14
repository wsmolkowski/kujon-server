# coding=UTF-8
# http://stackoverflow.com/questions/37068709/python-tornado-queue-toro-task-consuming-in-parallel

import logging
from datetime import datetime

import motor
from tornado import queues, gen
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options

from commons.config import Config
from commons.constants import fields, collections
from commons.enumerators import JobStatus, JobType
from crawler.UsosCrawler import UsosCrawler

QUEUE_MAXSIZE = 100
MAX_WORKERS = 4
SLEEP = 2

define('environment', default='development')


class MongoDbQueue(object):
    def __init__(self, config):
        self.config = config
        self.queue = queues.Queue(maxsize=QUEUE_MAXSIZE)
        self.db = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]
        self.processing = []

        logging.info(self.db)

    @gen.coroutine
    def load_work(self):

        # create jobs and put into queue
        cursor = self.db[collections.JOBS_QUEUE].find({fields.JOB_STATUS: JobStatus.PENDING.value})

        while (yield cursor.fetch_next):
            if len(self.processing) >= MAX_WORKERS:
                break
            job = cursor.next_object()
            logging.debug('putting job to queue for type: {0} queue size: {1}'.format(job[fields.JOB_TYPE],
                                                                                      self.queue.qsize()))
            yield self.queue.put(job)

        raise gen.Return()

    @gen.coroutine
    def update_job(self, job, status, message=None):
        # insert current job to history collection
        old = job.copy()
        old.pop(fields.MONGO_ID)
        yield self.db[collections.JOBS_LOG].insert(old)

        # change values and update
        job[fields.JOB_STATUS] = status
        job[fields.UPDATE_TIME] = datetime.now()
        job[fields.JOB_MESSAGE] = message

        update = yield self.db[collections.JOBS_QUEUE].update(
            {fields.MONGO_ID: job[fields.MONGO_ID]}, job)

        logging.debug(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[fields.MONGO_ID], status, update))

        raise gen.Return()

    @gen.coroutine
    def process_job(self, job):
        try:
            self.processing.append(job)
            logging.info("processing job: {0} with job type: {1} queue size: {2}".format(
                job[fields.MONGO_ID], job[fields.JOB_TYPE], self.queue.qsize()))
            yield self.update_job(job, JobStatus.START.value)

            if job[fields.JOB_TYPE] == JobType.INITIAL_USER_CRAWL.value:
                yield UsosCrawler(self.config).initial_user_crawl(job[fields.USER_ID])
            elif job[fields.JOB_TYPE] == JobType.REFRESH_USER_CRAWL.value:
                yield UsosCrawler(self.config).initial_user_crawl(job[fields.USER_ID], refresh=True)
            elif job[fields.JOB_TYPE] == JobType.SUBSCRIBE_USOS.value:
                yield UsosCrawler(self.config).subscribe(job[fields.USER_ID])
            elif job[fields.JOB_TYPE] == JobType.UNSUBSCRIBE_USOS.value:
                yield UsosCrawler(self.config).unsubscribe(job[fields.USER_ID])
            else:
                raise Exception("could not process job with unknown job type: {0}".format(job[fields.JOB_TYPE]))
            yield self.update_job(job, JobStatus.FINISH.value)

            logging.debug(
                "processed job: {0} with job type: {1}".format(job[fields.MONGO_ID], job[fields.JOB_TYPE]))
        finally:
            self.processing.remove(job)

    @gen.coroutine
    def worker(self):
        while True:
            try:
                job = yield self.queue.get()
                logging.debug("consuming queue job {0}. current queue size: {1} processing: {2}".format(
                    job, self.queue.qsize(), len(self.processing)))
                yield self.process_job(job)
            except Exception as ex:
                msg = "Exception while executing job {0} with: {1}".format(job[fields.MONGO_ID], ex)
                logging.exception(msg)
                yield self.update_job(job, JobStatus.FAIL.value, msg)
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

    config = Config(options.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)

    mongoQueue = MongoDbQueue(config)

    io_loop = IOLoop.current()
    io_loop.run_sync(mongoQueue.workers)
