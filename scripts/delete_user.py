# coding=UTF-8

import logging
import sys
from datetime import datetime

import pymongo

from commons import constants, utils
from commons.config import Config
from commons.enumerators import JobStatus
from commons.enumerators import JobType

utils.initialize_logging('delete_user')


def main(arguments):
    user_email = arguments[0]
    environment = arguments[1]

    client = None
    try:
        logging.info('deleting user by email: {0} in environment: {1}'.format(user_email, environment))

        config = Config(environment)
        client = pymongo.MongoClient(config.MONGODB_URI)
        db = client[config.MONGODB_NAME]

        user_doc = db[constants.COLLECTION_USERS].find_one(
            {constants.USER_EMAIL: user_email, constants.USOS_PAIRED: True})

        if not user_doc:
            raise Exception("user by email {0} not found.".format(user_email))

        result = db[constants.COLLECTION_USERS].delete_many({constants.USER_EMAIL: user_email})
        logging.info('removed user data by email: {0} resulted in {1}'.format(user_email, result))

        if user_doc[constants.USOS_PAIRED]:
            result = db[constants.COLLECTION_JOBS_QUEUE].insert_one({
                constants.USER_ID: user_doc[constants.MONGO_ID],
                constants.CREATED_TIME: datetime.now(),
                constants.UPDATE_TIME: None,
                constants.JOB_MESSAGE: None,
                constants.JOB_STATUS: JobStatus.PENDING.value,
                constants.JOB_TYPE: JobType.ARCHIVE_USER.value})

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
