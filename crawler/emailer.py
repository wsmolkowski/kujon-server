# coding=UTF-8

import asyncio
import logging
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

import motor.motor_asyncio
from tornado.options import define, options
from tornado.options import parse_command_line

from commons import constants
from commons.config import Config
from commons.enumerators import JobStatus
from crawler import email_factory

QUEUE_MAXSIZE = 100
# MAX_WORKERS = 4
SLEEP = 2

define('environment', default='development')


class Emailer(object):
    def __init__(self, config, loop=None):
        if not loop:
            loop = asyncio.get_event_loop()

        self.config = config
        self.loop = loop
        self.running = True
        self.queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE, loop=self.loop)
        self.db = motor.motor_asyncio.AsyncIOMotorClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]

        logging.info(self.db)

    def stop(self):
        self.running = False

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

        logging.debug(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[constants.MONGO_ID], status, update))

    async def produce(self):
        while self.running:
            cursor = self.db[constants.COLLECTION_EMAIL_QUEUE].find({constants.JOB_STATUS: JobStatus.PENDING.value})

            async for job in cursor:
                await self.queue.put(job)

            await asyncio.sleep(SLEEP)

    async def consume(self):
        while True:
            job = await self.queue.get()

            try:
                smtp = smtplib.SMTP()
                smtp.connect(self.config.SMTP_HOST, self.config.SMTP_PORT)
                # smtp.starttls()
                smtp.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)

                # process the item
                await self.update_job(job, JobStatus.START.value)

                msg = MIMEText(job[email_factory.SMTP_TEXT].encode(constants.ENCODING), _charset=constants.ENCODING)
                msg['Subject'] = Header(job[email_factory.SMTP_SUBJECT], constants.ENCODING)
                msg['From'] = job[email_factory.SMTP_FROM]
                msg['To'] = ','.join(job[email_factory.SMTP_TO])

                smtp.sendmail(job[email_factory.SMTP_FROM], job[email_factory.SMTP_TO], msg.as_string())

                await self.db[constants.COLLECTION_MESSAGES].insert({
                    constants.USER_ID: job[constants.USER_ID],
                    constants.CREATED_TIME: datetime.now(),
                    constants.FIELD_MESSAGE_FROM: self.config.PROJECT_TITLE,
                    constants.FIELD_MESSAGE_TYPE: 'email',
                    constants.FIELD_MESSAGE_TEXT: job[email_factory.SMTP_TEXT]
                })

                await self.update_job(job, JobStatus.FINISH.value)

                smtp.quit()
            except Exception as ex:
                print(ex)
                await self.update_job(job, JobStatus.FAIL.value)


if __name__ == '__main__':

    try:
        parse_command_line()
        config = Config(options.environment)
        logging.getLogger().setLevel(config.LOG_LEVEL)

        loop = asyncio.get_event_loop()
        runner = Emailer(config, loop)
        asyncio.ensure_future(runner.produce(), loop=loop)
        loop.run_until_complete(runner.consume())
    finally:
        if runner:
            runner.stop()

        loop.close()
