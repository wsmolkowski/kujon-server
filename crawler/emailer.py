# coding=UTF-8

import logging
import smtplib
from datetime import timedelta, datetime
from email.header import Header
from email.mime.text import MIMEText

import motor
from tornado import queues, gen, ioloop
from tornado.options import parse_command_line

from commons import settings, constants

QUEUE_MAXSIZE = 100
SLEEP = 1


class MongoEmailQueue(object):
    def __init__(self, queue_maxsize=QUEUE_MAXSIZE):
        super(MongoEmailQueue, self).__init__()

        self._queue = queues.Queue(maxsize=queue_maxsize)

        self.smtp = smtplib.SMTP()
        self.smtp.connect(settings.SMTP_HOST, settings.SMTP_PORT)
        self.smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        self._db = self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]

    @gen.coroutine
    def __load_work(self):

        # check if data for users should be updated
        delta = datetime.now() - timedelta(minutes=constants.CRAWL_USER_UPDATE)

        cursor = self._db[constants.COLLECTION_EMAIL_QUEUE].find(
            {constants.UPDATE_TIME: {'$lt': delta}, constants.JOB_STATUS: constants.JOB_FINISH}
        ).sort([(constants.UPDATE_TIME, -1)])

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            yield self.update_job(job, constants.JOB_PENDING)

        # create jobs and put into queue
        cursor = self._db[constants.COLLECTION_EMAIL_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (yield cursor.fetch_next):
            job = cursor.next_object()
            logging.debug('putting job to queue with ID: {0}'.format(job[constants.MONGO_ID]))
            yield self._queue.put(job)

    @gen.coroutine
    def update_job(self, job, status, message=None):
        # insert current job to history collection
        old = job.copy()
        old.pop(constants.MONGO_ID)
        yield self._db[constants.COLLECTION_EMAIL_QUEUE_LOG].insert(old)

        # change values and update
        job[constants.JOB_STATUS] = status
        job[constants.UPDATE_TIME] = datetime.now()
        job[constants.JOB_MESSAGE] = message

        update = yield self._db[constants.COLLECTION_EMAIL_QUEUE].update(
            {constants.MONGO_ID: job[constants.MONGO_ID]}, job)

        logging.debug(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    @gen.coroutine
    def process_job(self, job):
        logging.debug("processing job: {0}".format(job[constants.MONGO_ID]))

        msg = MIMEText(job[constants.SMTP_TEXT].encode(constants.ENCODING), 'plain', constants.ENCODING)
        msg['Subject'] = Header(job[constants.SMTP_SUBJECT], constants.ENCODING)
        msg['From'] = job[constants.SMTP_FROM]
        msg['To'] = ','.join(job[constants.SMTP_TO])

        self.smtp.sendmail(job[constants.SMTP_FROM], job[constants.SMTP_TO], msg.as_string())

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

    mq = MongoEmailQueue()

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(mq.worker)
