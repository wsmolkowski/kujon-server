# coding=UTF-8

import logging
from datetime import timedelta, datetime

import motor
from tornado import queues, gen, ioloop
from tornado.options import parse_command_line

from commons import settings, constants
from commons.usosutils.usoscrawler import UsosCrawler


class MongoDbQueue(object):

    def __init__(self):
        super(MongoDbQueue, self).__init__()

        self.crawler = UsosCrawler()
        self.queue = queues.Queue(maxsize=constants.WORKES_QUEUE_SIZE)
        self.db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]
        self.processing = []

    @gen.coroutine
    def load_work(self):

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
            logging.debug(
                'putting job user: {0} type: {1} queue size: {2} processing {3}'.format(job[constants.USER_ID],
                                                                                        job[constants.JOB_TYPE],
                                                                                        self.queue.qsize(),
                                                                                        len(self.processing)))

            yield self.queue.put(job)

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

        logging.debug(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    @gen.coroutine
    def remove_user_data(self, user_id):
        logging.debug('removing user data for user_id {0}'.format(user_id))

        collections = yield self.db.collection_names()

        for collection in collections:

            if collection == constants.COLLECTION_USERS_ARCHIVE:
                continue

            exists = yield self.db[collection].find_one({constants.USER_ID: {'$exists': True, '$ne': False}})
            if exists:
                result = yield self.db[collection].remove({constants.USER_ID: user_id})
                logging.debug('removed data from collection {0} for user {1} with result {2}'.format(
                    collection, user_id, result))

        logging.debug('removed user data for user_id {0}'.format(user_id))

    @gen.coroutine
    def process_job(self, job):
        try:
            logging.info("processing job: {0} with job type: {1} queue size: {2} parallel processing: {3}".format(
                job[constants.MONGO_ID], job[constants.JOB_TYPE], self.queue.qsize(), len(self.processing)))
            self.processing.append(job)

            yield self.update_job(job, constants.JOB_START)

            if job[constants.JOB_TYPE] == 'initial_user_crawl':
                yield self.crawler.initial_user_crawl(job[constants.USER_ID])
            elif job[constants.JOB_TYPE] == 'update_user_crawl':
                yield self.crawler.update_user_crawl(job[constants.USER_ID])
            elif job[constants.JOB_TYPE] == 'archive_user':
                yield self.remove_user_data(job[constants.USER_ID])
            elif job[constants.JOB_TYPE] == 'unsubscribe_usos':
                yield self.crawler.unsubscribe(job[constants.USER_ID])
            else:
                raise Exception("could not process job with unknown job type: {0}".format(job[constants.JOB_TYPE]))

            yield self.update_job(job, constants.JOB_FINISH)

            logging.info(
                "processed job: {0} with job type: {1}  queue size: {2}".format(
                    job[constants.MONGO_ID], job[constants.JOB_TYPE], self.queue.qsize()))
        finally:
            self.processing.remove(job)

    @gen.coroutine
    def worker(self):
        while True:
            if self.queue.empty() or len(self.processing) >= constants.WORKERS_MAX:
                yield gen.sleep(constants.WORKERS_SLEEP)
            else:
                try:
                    job = yield self.queue.get()
                    logging.debug("consuming queue job {0}. current queue size: {1} parallel processing: {2}".format(
                        job, self.queue.qsize(), len(self.processing)))
                    yield self.process_job(job)
                except Exception, ex:
                    msg = "Exception while executing job {0} with: {1}".format(job[constants.MONGO_ID], ex.message)
                    logging.exception(msg)
                    yield self.update_job(job, constants.JOB_FAIL, msg)
                finally:
                    self.queue.task_done()

    @gen.coroutine
    def producer(self):
        while True:
            yield self.load_work()
            yield gen.sleep(constants.WORKERS_SLEEP)

    @gen.coroutine
    def workers(self):
        ioloop.IOLoop.current().spawn_callback(self.producer)
        futures = [self.worker() for _ in range(constants.WORKERS_MAX)]
        yield futures


if __name__ == '__main__':
    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    mongoQueue = MongoDbQueue()

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(mongoQueue.workers)
