# coding=UTF-8

import logging
import sys

import pymongo

from commons import utils
from commons.config import Config
from commons.constants import fields, collections


def main(arguments):
    user_email = arguments[0]
    environment = arguments[1]

    client = None
    try:
        logging.info('deleting user by email: {0} in environment: {1}'.format(user_email, environment))

        config = Config(environment)
        utils.initialize_logging('delete_user', log_dir=config.LOG_DIR)
        client = pymongo.MongoClient(config.MONGODB_URI)

        db = client[config.MONGODB_NAME]

        user_doc = db[collections.USERS].find_one({fields.USER_EMAIL: user_email})

        if not user_doc:
            raise Exception("user by email {0} not found.".format(user_email))

        result = db[collections.USERS].delete_many({fields.USER_EMAIL: user_email})
        logging.info('removed user data by email: {0} resulted in {1}'.format(user_email, result))

        if fields.USOS_PAIRED in user_doc and user_doc[fields.USOS_PAIRED]:
            # result = db[collections.JOBS_QUEUE].insert_one({
            #     fields.USER_ID: user_doc[fields.MONGO_ID],
            #     fields.CREATED_TIME: datetime.now(),
            #     fields.UPDATE_TIME: None,
            #     fields.JOB_MESSAGE: None,
            #     fields.JOB_STATUS: JobStatus.PENDING.value,
            #     fields.JOB_TYPE: JobType.ARCHIVE_USER.value})

            logging.info('created job for cleaning user USOS data resulted in {0}'.format(result))

        logging.info('removing ok')
    except Exception as ex:
        logging.exception(ex)

    finally:
        if client:
            client.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exc_info('Provide 2 parameters: email environment')

    main(sys.argv[1:])
