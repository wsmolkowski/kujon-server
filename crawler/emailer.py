# coding=UTF-8

import asyncio
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import motor.motor_asyncio
from tornado.options import define, options
from tornado.options import parse_command_line

from commons.config import Config
from commons.constants import fields, collections
from commons.enumerators import JobStatus
from commons.mixins import EmailMixin

QUEUE_MAXSIZE = 100
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
        old.pop(fields.MONGO_ID)
        await self.db[collections.EMAIL_QUEUE_LOG].insert(old)

        # change values and update
        job[fields.JOB_STATUS] = status
        job[fields.UPDATE_TIME] = datetime.now()
        if message:
            job[fields.JOB_MESSAGE] = message

        update = await self.db[collections.EMAIL_QUEUE].update(
            {fields.MONGO_ID: job[fields.MONGO_ID]}, job)

        logging.debug(
            "updated job: {0} with status: {1} resulted in: {2}".format(job[fields.MONGO_ID], status, update))

    async def produce(self):
        while self.running:
            cursor = self.db[collections.EMAIL_QUEUE].find({fields.JOB_STATUS: JobStatus.PENDING.value})

            async for job in cursor:
                await self.queue.put(job)

            await asyncio.sleep(SLEEP)

    async def consume(self):
        while True:
            job = await self.queue.get()

            try:
                smtp = smtplib.SMTP()
                smtp.connect(self.config.SMTP_HOST, self.config.SMTP_PORT)
                smtp.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)

                # process the item
                await self.update_job(job, JobStatus.START.value)

                msg = MIMEMultipart('alternative')

                msg['Subject'] = '[{0}] {1}'.format(self.config.PROJECT_TITLE, job[EmailMixin.SMTP_SUBJECT])
                msg['From'] = job[EmailMixin.SMTP_FROM]
                msg['To'] = ','.join(job[EmailMixin.SMTP_TO])

                msg.attach(MIMEText(job[EmailMixin.SMTP_TEXT], 'plain'))
                msg.attach(MIMEText(job[EmailMixin.SMTP_HTML], 'html'))

                smtp.sendmail(job[EmailMixin.SMTP_FROM], job[EmailMixin.SMTP_TO], msg.as_string())

                logging.debug('email sent to {0}'.format(job[EmailMixin.SMTP_TO]))

                msg_doc = await self.db[collections.MESSAGES].insert({
                    fields.USER_ID: job[fields.USER_ID],
                    fields.CREATED_TIME: datetime.now(),
                    fields.FIELD_MESSAGE_FROM: self.config.PROJECT_TITLE,
                    fields.FIELD_MESSAGE_TYPE: 'email',
                    fields.JOB_MESSAGE: job[EmailMixin.SMTP_TEXT]
                })

                logging.debug(msg_doc)

                await self.update_job(job, JobStatus.FINISH.value)

                smtp.quit()
            except Exception as ex:
                logging.exception(ex)
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
