# coding=UTF-8

import logging
import sys

import pymongo
from tornado.options import parse_command_line

from commons import utils
from commons.config import Config
from commons.constants import fields, collections
from commons.enumerators import Environment


def remove_user_data(user_id, client):
    for collection in client.collection_names(include_system_collections=False):
        if collection in (collections.USERS,):
            continue

        exists = client[collection].find_one({fields.USER_ID: {'$exists': True, '$ne': False}})
        if exists:
            client[collection].remove({fields.USER_ID: user_id})


def copy_user_credentials(email_from, email_to, config_from, config_to):
    try:

        client_from = pymongo.MongoClient(config_from.MONGODB_URI)
        db_from = client_from[config_from.MONGODB_NAME]
        client_to = pymongo.MongoClient(config_to.MONGODB_URI)
        db_to = client_to[config_to.MONGODB_NAME]

        user_from_doc = db_from[collections.USERS].find_one({
            fields.USER_EMAIL: email_from, fields.USOS_PAIRED: True})
        if not user_from_doc:
            raise Exception("user from {0} not found.".format(email_from))

        logging.info('user_from_doc: {0}'.format(user_from_doc))

        user_to_doc = db_to[collections.USERS].find_one({
            fields.USER_EMAIL: email_to, fields.USOS_PAIRED: True})
        if not user_to_doc:
            raise Exception("user to {0} not found.".format(email_to))

        logging.info('user_to_doc: {0}'.format(user_to_doc))

        remove_user_data(user_to_doc[fields.MONGO_ID], db_to)

        logging.info('removed user to data')

        user_to_doc[fields.ACCESS_TOKEN_KEY] = user_from_doc[fields.ACCESS_TOKEN_KEY]
        user_to_doc[fields.ACCESS_TOKEN_SECRET] = user_from_doc[fields.ACCESS_TOKEN_SECRET]
        user_to_doc[fields.USOS_ID] = user_from_doc[fields.USOS_ID]

        if fields.USOS_USER_ID in user_from_doc:
            user_to_doc[fields.USOS_USER_ID] = user_from_doc[fields.USOS_USER_ID]

        updated = db_to[collections.USERS].update(
            {fields.MONGO_ID: user_to_doc[fields.MONGO_ID]}, user_to_doc)

        logging.info('collection: {0} updated: {1}'.format(collections.USERS, updated))

    finally:
        if client_from:
            client_from.close()
        if client_to:
            client_to.close()


def main(arguments):
    email_from = arguments[0]
    email_to = arguments[1]
    environment_from = arguments[2]
    environment_to = arguments[3]

    if environment_to == Environment.PRODUCTION.value:
        raise Exception('Can not copy values to {0} environment. :('.format(Environment.PRODUCTION.value))

    config_from = Config(environment_from)
    config_to = Config(environment_to)

    utils.initialize_logging('resubscribe_users', log_dir=config_to.LOG_DIR)

    logging.info('copying from email: {0} (environment: {1}) to email: {2} (environment {3})'.format(
        email_from, environment_from, email_to, environment_to
    ))

    try:
        copy_user_credentials(email_from=email_from, email_to=email_to, config_from=config_from,
                              config_to=config_to)

        print('copying ok')
    except Exception as ex:
        logging.exception(ex)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exc_info('Provide 4 parameters: email_from email_to environment_from environment_to')

    parse_command_line()

    main(sys.argv[1:])
