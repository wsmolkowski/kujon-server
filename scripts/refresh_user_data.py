# coding=utf-8

import logging

import motor.motor_tornado
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options

from commons import constants, utils
from commons.config import Config
from crawler import job_factory

define('environment', default='development')


async def main():
    config = Config(options.environment)
    utils.initialize_logging('refresh_user_data', log_dir=config.LOG_DIR)
    db = motor.motor_tornado.MotorClient(config.MONGODB_URI)[config.MONGODB_NAME]

    cursor = db[constants.COLLECTION_USERS].find({constants.USOS_PAIRED: True})
    async for user_doc in cursor:
        try:
            logging.info('create refresh job for user {0}'.format(user_doc[constants.MONGO_ID]))

            result = await db[constants.COLLECTION_JOBS_QUEUE].insert(
                job_factory.refresh_user_job(user_doc[constants.MONGO_ID]))

            logging.info('created job with {0}'.format(result))

        except Exception as ex:
            logging.exception(ex)


if __name__ == '__main__':
    parse_command_line()

    logging.getLogger().setLevel(logging.DEBUG)

    IOLoop.current().run_sync(main)
