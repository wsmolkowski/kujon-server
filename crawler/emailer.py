# coding=UTF-8

import logging
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

import motor
from tornado import queues, gen
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line

from commons import settings, constants

QUEUE_MAXSIZE = 100
MAX_WORKERS = 4
SLEEP = 2


class EmailQueue(object):
    def __init__(self):
        self.queue = queues.Queue(maxsize=QUEUE_MAXSIZE)
        self.db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)[settings.MONGODB_NAME]
        self.processing = []

        logging.info(self.db)

    @gen.coroutine
    def load_work(self):
        # try re-run failed jobs
        # delta = datetime.now() - timedelta(minutes=60)
        #
        # cursor = self.db[constants.COLLECTION_EMAIL_QUEUE].find({
        #     constants.UPDATE_TIME: {'$lt': delta}, constants.JOB_STATUS: constants.JOB_FAIL}). \
        #     sort([(constants.UPDATE_TIME, -1)])
        #
        # while (yield cursor.fetch_next):
        #     job = cursor.next_object()
        #     yield self.update_job(job, constants.JOB_PENDING)

        # create jobs and put into queue
        cursor = self.db[constants.COLLECTION_EMAIL_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (yield cursor.fetch_next):
            if len(self.processing) >= MAX_WORKERS:
                break
            job = cursor.next_object()
            yield self.queue.put(job)

        raise gen.Return(None)

    @gen.coroutine
    def update_job(self, job, status, message=None):
        # insert current job to history collection
        old = job.copy()
        old.pop(constants.MONGO_ID)
        yield self.db[constants.COLLECTION_EMAIL_QUEUE_LOG].insert(old)

        # change values and update
        job[constants.JOB_STATUS] = status
        job[constants.UPDATE_TIME] = datetime.now()
        job[constants.JOB_MESSAGE] = message

        update = yield self.db[constants.COLLECTION_EMAIL_QUEUE].update(
            {constants.MONGO_ID: job[constants.MONGO_ID]}, job)

        logging.info(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    @gen.coroutine
    def process_job(self, job):
        smtp = smtplib.SMTP()

        try:
            self.processing.append(job)
            logging.info("processing job: {0}".format(job[constants.MONGO_ID]))

            smtp.connect(settings.SMTP_HOST, settings.SMTP_PORT)
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            yield self.update_job(job, constants.JOB_START)

            msg = MIMEText(job[constants.SMTP_TEXT].encode(constants.ENCODING), 'plain', constants.ENCODING)
            msg['Subject'] = Header(job[constants.SMTP_SUBJECT], constants.ENCODING)
            msg['From'] = job[constants.SMTP_FROM]
            msg['To'] = ','.join(job[constants.SMTP_TO])

            smtp.sendmail(job[constants.SMTP_FROM], job[constants.SMTP_TO], msg.as_string())

            yield self.update_job(job, constants.JOB_FINISH)

            logging.info("processed job: {0}".format(job[constants.MONGO_ID]))
        finally:
            smtp.quit()
            self.processing.remove(job)

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


if __name__ == '__main__':
    parse_command_line()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    emailQueue = EmailQueue()

    io_loop = IOLoop.current()
    io_loop.run_sync(emailQueue.workers)
