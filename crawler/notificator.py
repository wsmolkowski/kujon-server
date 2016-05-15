# coding=UTF-8

# https://documentation.onesignal.com/docs/notifications-create-notification

import json
import logging
from datetime import timedelta, datetime

import motor
from tornado import queues, gen
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line

from commons import settings, constants, utils

QUEUE_MAXSIZE = 100
MAX_WORKERS = 4
SLEEP = 2


class NotificatorQueue(object):
    _PROJECT_TITLE = settings.PROJECT_TITLE
    _NOTIFICATION_ID = settings.APPLICATION_ID
    _NOTIFICATION_URL = settings.NOTIFICATION_URL

    def __init__(self):
        self.queue = queues.Queue(maxsize=QUEUE_MAXSIZE)
        self.db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]
        self.processing = []

        logging.info(self.db)

    @gen.coroutine
    def load_work(self):

        # not_all = notification_all()
        # try:
        #     d = yield self._db[constants.COLLECTION_NOTIFICATION_QUEUE].insert(not_all)
        #     logging.info(d)
        # except Exception, ex:
        #     print ex

        # check if data for users should be updated
        delta = datetime.now() - timedelta(minutes=constants.CRAWL_USER_UPDATE)

        cursor = self.db[constants.COLLECTION_NOTIFICATION_QUEUE].find(
            {constants.UPDATE_TIME: {'$lt': delta}, constants.JOB_STATUS: constants.JOB_FINISH}
        ).sort([(constants.UPDATE_TIME, -1)])

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            yield self.update_job(job, constants.JOB_PENDING)

        # create jobs and put into queue
        cursor = self.db[constants.COLLECTION_NOTIFICATION_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (yield cursor.fetch_next):
            if len(self.processing) >= MAX_WORKERS:
                break
            job = cursor.next_object()
            logging.info('putting job to queue for user: {0} type: {1} queue size: {2}'.format(job[constants.USER_ID],
                                                                                               job[constants.JOB_TYPE],
                                                                                               self.queue.qsize()))
            yield self.queue.put(job)

        raise gen.Return(None)

    @gen.coroutine
    def update_job(self, job, status, message=None):
        # insert current job to history collection
        old = job.copy()
        old.pop(constants.MONGO_ID)
        yield self.db[constants.COLLECTION_NOTIFICATION_QUEUE_LOG].insert(old)

        # change values and update
        job[constants.JOB_STATUS] = status
        job[constants.UPDATE_TIME] = datetime.now()
        job[constants.JOB_MESSAGE] = message

        update = yield self.db[constants.COLLECTION_NOTIFICATION_QUEUE].update(
            {constants.MONGO_ID: job[constants.MONGO_ID]}, job)

        logging.info(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    @gen.coroutine
    def process_job(self, job):
        try:
            self.processing.append(job)

            logging.info("processing job: {0}".format(job[constants.MONGO_ID]))
            yield self.update_job(job, constants.JOB_START)
            client = utils.http_client()

            headers = HTTPHeaders({
                'Authorization': 'Basic M2Q0NmNkNDUtOTFiMy00OTA2LTlkZGMtNWVhZDFjNGM4ODcw',
                'Content-Type': 'application/json',
                'User-Agent': self._PROJECT_TITLE
            })

            body = {
                'app_id': self._NOTIFICATION_ID,
                'included_segments': ['All'],
                'contents': {'en': 'Testowa notyfikacja'}
            }

            request = HTTPRequest(self._NOTIFICATION_URL, body=json.dumps(body), method='POST', headers=headers)

            response = yield client.fetch(request)
            response = json.loads(response.body)

            yield self.update_job(job, constants.JOB_FINISH)

            logging.info("processed job: {0} with result {1}".format(job[constants.MONGO_ID], response))
        finally:
            self.processing.remove(job)

        raise gen.Return(None)

    @gen.coroutine
    def worker(self):

        while True:
            try:
                job = yield self.queue.get()
                logging.info("consuming queue job {0}. current queue size: {1} processing: {2}".format(
                    job, self.queue.qsize(), len(self.processing)))
                yield self.process_job(job)
            except Exception, ex:
                msg = "Exception while executing job with: {1}".format(job[constants.MONGO_ID], ex.message)
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


def notification_user(user_id, message=None):
    return {
        constants.USER_ID: user_id,
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_MESSAGE: message,
        constants.JOB_STATUS: constants.JOB_PENDING,
    }


def notification_all(message=None):
    return {
        constants.USER_ID: None,
        constants.CREATED_TIME: datetime.now(),
        constants.UPDATE_TIME: None,
        constants.JOB_MESSAGE: message,
        constants.JOB_STATUS: constants.JOB_PENDING,
    }


if __name__ == '__main__':
    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    notificatorQueue = NotificatorQueue()

    io_loop = IOLoop.current()
    io_loop.run_sync(notificatorQueue.workers)
