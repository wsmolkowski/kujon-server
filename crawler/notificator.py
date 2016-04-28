# coding=UTF-8

import json
import logging
from datetime import timedelta, datetime

import motor
from tornado import queues, gen, ioloop
from tornado.httputil import HTTPHeaders
from tornado.options import parse_command_line

from commons import settings, constants, utils

QUEUE_MAXSIZE = 100
SLEEP = 1


class NotificatorQueue(object):
    _PROJECT_TITLE = settings.PROJECT_TITLE
    _NOTIFICATION_ID = settings.APPLICATION_ID
    _NOTIFICATION_URL = settings.NOTIFICATION_URL

    def __init__(self, queue_maxsize=QUEUE_MAXSIZE):
        super(NotificatorQueue, self).__init__()

        self._queue = queues.Queue(maxsize=queue_maxsize)
        self._db = self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]

    @gen.coroutine
    def __load_work(self):

        # check if data for users should be updated
        delta = datetime.now() - timedelta(minutes=constants.CRAWL_USER_UPDATE)

        cursor = self._db[constants.COLLECTION_NOTIFICATION_QUEUE].find(
            {constants.UPDATE_TIME: {'$lt': delta}, constants.JOB_STATUS: constants.JOB_FINISH}
        ).sort([(constants.UPDATE_TIME, -1)])

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            yield self.update_job(job, constants.JOB_PENDING)

        # create jobs and put into queue
        cursor = self._db[constants.COLLECTION_NOTIFICATION_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            logging.debug('putting job to queue with ID: {0}'.format(job[constants.MONGO_ID]))
            yield self._queue.put(job)

    @gen.coroutine
    def update_job(self, job, status, message=None):
        # insert current job to history collection
        old = job.copy()
        old.pop(constants.MONGO_ID)
        yield self._db[constants.COLLECTION_NOTIFICATION_QUEUE_LOG].insert(old)

        # change values and update
        job[constants.JOB_STATUS] = status
        job[constants.UPDATE_TIME] = datetime.now()
        job[constants.JOB_MESSAGE] = message

        update = yield self._db[constants.COLLECTION_NOTIFICATION_QUEUE].update(
            {constants.MONGO_ID: job[constants.MONGO_ID]}, job)

        logging.debug(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    @gen.coroutine
    def process_job(self, job):
        logging.debug("processing job: {0}".format(job[constants.MONGO_ID]))

        client = utils.http_client()

        headers = HTTPHeaders({
            'Authorization: Basic': 'M2Q0NmNkNDUtOTFiMy00OTA2LTlkZGMtNWVhZDFjNGM4ODcw',
            'Content-Type': 'application/json',
            'User-Agent': self._PROJECT_TITLE
        })

        body = {
            'app_id': self._NOTIFICATION_ID,
            'included_segments': ['All'],
            'contents': {'en': 'Testowa notyfikacja'}
        }

        request = client.HTTPRequest(self._NOTIFICATION_URL, body=json.dumps(body), method='POST', headers=headers)

        response = yield client.fetch(request)

        logging.debug(response)

        logging.debug("processed job: {0}".format(job[constants.MONGO_ID]))

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
                    msg = "Exception while executing job with: {1}".format(job[constants.MONGO_ID], ex.message)
                    logging.exception(msg)

                    yield self.update_job(job, constants.JOB_FAIL, msg)
                finally:
                    self._queue.task_done()


if __name__ == '__main__':
    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    mq = NotificatorQueue()

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(mq.worker)
