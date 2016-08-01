# coding=UTF-8

import asyncio
import logging
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

import motor
from tornado import queues, gen
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.options import parse_command_line

from commons import constants
from commons.config import Config

QUEUE_MAXSIZE = 100
MAX_WORKERS = 4
SLEEP = 2

define('environment', default='development')


class EmailQueue(object):
    def __init__(self, config):
        self.config = config
        self.queue = queues.Queue(maxsize=QUEUE_MAXSIZE)
        self.db = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]
        self.processing = []

        logging.info(self.db)

    async def load_work(self):
        # try re-run failed jobs
        # delta = datetime.now() - timedelta(minutes=60)
        #
        # cursor = self.db[constants.COLLECTION_EMAIL_QUEUE].find({
        #     constants.UPDATE_TIME: {'$lt': delta}, constants.JOB_STATUS: constants.JOB_FAIL}). \
        #     sort([(constants.UPDATE_TIME, -1)])
        #
        # while (await cursor.fetch_next):
        #     job = cursor.next_object()
        #     await self.update_job(job, constants.JOB_PENDING)

        # create jobs and put into queue
        cursor = self.db[constants.COLLECTION_EMAIL_QUEUE].find({constants.JOB_STATUS: constants.JOB_PENDING})

        while (await cursor.fetch_next):
            if len(self.processing) >= MAX_WORKERS:
                break
            job = cursor.next_object()
            await self.queue.put(job)

    async def update_job(self, job, status, message=None):
        # insert current job to history collection
        old = job.copy()
        old.pop(constants.MONGO_ID)
        await self.db[constants.COLLECTION_EMAIL_QUEUE_LOG].insert(old)

        # change values and update
        job[constants.JOB_STATUS] = status
        job[constants.UPDATE_TIME] = datetime.now()
        job[constants.JOB_MESSAGE] = message

        update = await self.db[constants.COLLECTION_EMAIL_QUEUE].update(
            {constants.MONGO_ID: job[constants.MONGO_ID]}, job)

        logging.info(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    async def process_job(self, job):
        smtp = smtplib.SMTP()

        try:
            self.processing.append(job)
            logging.info("processing job: {0}".format(job[constants.MONGO_ID]))

            smtp.connect(self.config.SMTP_HOST, self.config.SMTP_PORT)
            smtp.starttls()
            smtp.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)

            await self.update_job(job, constants.JOB_START)

            msg = MIMEText(job[constants.SMTP_TEXT].encode(constants.ENCODING), _charset=constants.ENCODING)
            msg['Subject'] = Header(job[constants.SMTP_SUBJECT], constants.ENCODING)
            msg['From'] = job[constants.SMTP_FROM]
            msg['To'] = ','.join(job[constants.SMTP_TO])

            smtp.sendmail(job[constants.SMTP_FROM], job[constants.SMTP_TO], msg.as_string())

            await self.db[constants.COLLECTION_MESSAGES].insert({
                constants.CREATED_TIME: datetime.now(),
                constants.FIELD_MESSAGE_FROM: self.config.PROJECT_TITLE,
                constants.FIELD_MESSAGE_TYPE: 'email',
                constants.FIELD_MESSAGE_TEXT: job[constants.SMTP_TEXT]
            })

            await self.update_job(job, constants.JOB_FINISH)

            logging.info("processed job: {0}".format(job[constants.MONGO_ID]))
        finally:
            smtp.quit()
            self.processing.remove(job)

    async def worker(self):

        while True:
            try:
                job = await self.queue.get()
                logging.info("consuming queue job {0}. current queue size: {1} processing: {2}".format(
                    job, self.queue.qsize(), len(self.processing)))
                await self.process_job(job)
            except Exception as ex:
                msg = "Exception while executing job with: {1}".format(job[constants.MONGO_ID], ex.message)
                logging.exception(msg)
                await self.update_job(job, constants.JOB_FAIL, msg)
            finally:
                self.queue.task_done()

    async def producer(self):
        while True:
            await self.load_work()
            await asyncio.sleep(SLEEP)

    async def workers(self):
        IOLoop.current().spawn_callback(self.producer)
        futures = [self.worker() for _ in range(MAX_WORKERS)]
        await gen.multi(futures)


if __name__ == '__main__':
    parse_command_line()
    config = Config(options.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)

    emailQueue = EmailQueue(config)

    io_loop = IOLoop.current()
    io_loop.run_sync(emailQueue.workers)
