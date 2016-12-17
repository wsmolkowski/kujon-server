# coding=UTF-8

import argparse
import logging
import sys
from datetime import datetime

import pymongo

from commons import constants, usosinstances, utils
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.enumerators import Environment
from commons.enumerators import ExceptionTypes
from crawler import job_factory


class DbUtils(object):
    INDEXED_FIELDS = (constants.USOS_ID, constants.USER_ID, constants.COURSE_ID, constants.TERM_ID, constants.ID,
                      constants.UNIT_ID, constants.GROUP_ID, constants.PROGRAMME_ID, constants.FACULTY_ID,
                      constants.USOS_PAIRED, constants.USER_EMAIL, constants.NODE_ID)

    def __init__(self, config, encrypt_usoses_keys=False):
        if config:
            self.config = config
            self.encrypt_usoses_keys = encrypt_usoses_keys
            self.client = pymongo.MongoClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]

            utils.initialize_logging('dbutils', log_dir=self.config.LOG_DIR)
            logging.info(self.client)

    def _ttl_index(self, collection, field, after_seconds):
        try:
            ttl_index = self.client[constants.COLLECTION_TOKENS].create_index(field, expireAfterSeconds=after_seconds)
            logging.info('created ttl index {0} on collection {1} and field {2} after_seconds {3}'.format(
                ttl_index, collection, field, after_seconds))
        except Exception as ex:
            logging.exception(ex)

    def _unique_index(self, collection, fields):
        try:
            index = self.client[collection].create_index(fields, unique=True)

            logging.info('unique index: {0} created on collection: {1} and fields {2}'.format(
                index, collection, fields))
        except Exception as ex:
            logging.exception(ex)

    def _unique_indexes(self):
        self._unique_index(constants.COLLECTION_USERS_INFO,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_TERMS,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.TERM_ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_FACULTIES,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.FACULTY_ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_PROGRAMMES,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.PROGRAMME_ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_COURSES,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.COURSE_ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_COURSES_EDITIONS, [(constants.USER_ID, pymongo.ASCENDING)])

        self.client[constants.COLLECTION_COURSES_CLASSTYPES].create_index(constants.USOS_ID, unique=True)

    def create_indexes(self):
        for collection in self.client.collection_names(include_system_collections=False):
            for field in self.INDEXED_FIELDS:
                if self.client[collection].find_one({field: {'$exists': True, '$ne': False}}):
                    try:
                        index = self.client[collection].create_index(field)
                        logging.info(
                            'created index {0} on collection {1} and field {2}'.format(index, collection, field))
                    except Exception as ex:
                        logging.exception(ex)

        self._ttl_index(constants.COLLECTION_TOKENS, constants.CREATED_TIME, constants.SECONDS_HOUR)
        self._ttl_index(constants.COLLECTION_COURSES_CLASSTYPES, constants.CREATED_TIME, constants.SECONDS_DAY)

        self._unique_indexes()

    def reindex(self):
        for collection in self.client.collection_names(include_system_collections=False):
            ri = self.client[collection].reindex()
            logging.info('collection {0} reindexed: {1}'.format(collection, ri))

    def drop_collections(self, skip_collections=None):
        if not skip_collections:
            skip_collections = list()
        db = self.client

        for collection in db.collection_names(include_system_collections=False):
            if collection in skip_collections:
                logging.info('skipping collection: {0}'.format(collection))
                continue
            db.drop_collection(collection)

    def recreate_database(self, aes_secret):
        try:
            now = datetime.now()
            aes = AESCipher(aes_secret)
            self.client.drop_collection(constants.COLLECTION_USOSINSTANCES)
            for usos in usosinstances.USOSINSTANCES:
                usos[constants.CREATED_TIME] = now
                logging.debug("adding usos: %r ", usos[constants.USOS_ID])
                doc = self.client.usosinstances.find_one({constants.USOS_ID: usos[constants.USOS_ID]})
                if not doc:
                    if self.encrypt_usoses_keys:
                        self.client[constants.COLLECTION_USOSINSTANCES].insert(aes.encrypt_usos(usos))
                    else:
                        self.client[constants.COLLECTION_USOSINSTANCES].insert(usos)
        except Exception as ex:
            logging.exception(ex)

    def remove_user_data(self, user_id, client=False):
        if not client:
            client = self.db

        for collection in client.collection_names(include_system_collections=False):
            if collection in (constants.COLLECTION_USERS,):
                continue

            exists = client[collection].find_one({constants.USER_ID: {'$exists': True, '$ne': False}})
            if exists:
                client[collection].remove({constants.USER_ID: user_id})

    def copy_user_credentials(self, email_from, email_to, environment_from, environment_to='demo'):

        try:
            if environment_to == Environment.PRODUCTION.value:
                raise Exception('Can not copy values to {0} environment. :('.format(Environment.PRODUCTION.value))

            self.config_from = Config(environment_from)
            self.config_to = Config(environment_to)

            self.client_from = pymongo.MongoClient(self.config_from.MONGODB_URI)
            self.db_from = self.client_from[self.config_from.MONGODB_NAME]
            self.client_to = pymongo.MongoClient(self.config_to.MONGODB_URI)
            self.db_to = self.client_to[self.config_to.MONGODB_NAME]

            user_from_doc = self.db_from[constants.COLLECTION_USERS].find_one({
                constants.USER_EMAIL: email_from, constants.USOS_PAIRED: True})
            if not user_from_doc:
                raise Exception("user from {0} not found.".format(email_from))

            logging.info('user_from_doc: {0}'.format(user_from_doc))

            user_to_doc = self.db_to[constants.COLLECTION_USERS].find_one({
                constants.USER_EMAIL: email_to, constants.USOS_PAIRED: True})
            if not user_from_doc:
                raise Exception("user to {0} not found.".format(email_to))

            logging.info('user_to_doc: {0}'.format(user_to_doc))

            self.remove_user_data(user_to_doc[constants.MONGO_ID], self.db_to)
            logging.info('removed user to data')

            user_to_doc[constants.ACCESS_TOKEN_KEY] = user_from_doc[constants.ACCESS_TOKEN_KEY]
            user_to_doc[constants.ACCESS_TOKEN_SECRET] = user_from_doc[constants.ACCESS_TOKEN_SECRET]
            user_to_doc[constants.USOS_ID] = user_from_doc[constants.USOS_ID]

            if constants.USOS_USER_ID in user_from_doc:
                user_to_doc[constants.USOS_USER_ID] = user_from_doc[constants.USOS_USER_ID]

            updated = self.db_to[constants.COLLECTION_USERS].update(
                {constants.MONGO_ID: user_to_doc[constants.MONGO_ID]}, user_to_doc)

            logging.info('collection: {0} updated: {1}'.format(constants.COLLECTION_USERS, updated))

            self.db_to[constants.COLLECTION_JOBS_QUEUE].insert(
                job_factory.refresh_user_job(user_to_doc[constants.MONGO_ID]))

            logging.info('created refresh task for updated user')

        finally:
            if self.client_from:
                self.client_from.close()
            if self.client_to:
                self.client_to.close()

    def refresh_failures(self):
        '''
            for each distinct user_id for exception  type - API
            cleanup exception collection for each user_id
            create refresh user job for each user user_id
        '''

        try:
            user_ids = self.client[constants.COLLECTION_EXCEPTIONS].find({'exception_type': ExceptionTypes.API.value}) \
                .distinct(constants.USER_ID)

            for user_id in user_ids:
                if not user_id:
                    continue

                user_doc = self.client[constants.COLLECTION_USERS].find_one(
                    {constants.MONGO_ID: user_id, constants.USOS_PAIRED: True})
                if not user_doc:
                    continue

                self.client[constants.COLLECTION_EXCEPTIONS].remove({constants.USER_ID: user_id})
                logging.info('removed exception data for user_id {0}'.format(user_id))

                self.client[constants.COLLECTION_JOBS_QUEUE].insert(job_factory.refresh_user_job(user_id))
                logging.info('created refresh task for user_id {0}'.format(user_id))

        except Exception as ex:
            logging.exception(ex)

    def recall_subscribe(self):
        '''
            for each paired user check if subscription collection is filled otherwise subscribe job is created
        :return:
        '''

        try:
            user_ids = self.client[constants.COLLECTION_USERS].find({constants.USOS_PAIRED: True}).distinct(
                constants.USER_ID)

            for user_id in user_ids:
                if not user_id:
                    continue

                logging.info('processing: {0}'.format(user_id))

                subsctiption_count = self.client[constants.COLLECTION_SUBSCRIPTIONS].find(
                    {constants.USER_ID: user_id}).count()

                if subsctiption_count == 3:  # 'crstests/user_grade', 'grades/grade', 'crstests/user_point'
                    continue

                self.client[constants.COLLECTION_JOBS_QUEUE].insert(job_factory.subscribe_user_job(user_id))
                logging.info('created subscribe task for user_id {0}'.format(user_id))

        except Exception as ex:
            logging.exception(ex)


##################################################################

parser = argparse.ArgumentParser(
    description="Script for local mongo database manipulation.",
    epilog="pretty neat, huh?",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument('-c', '--clean', action='store_const', dest='option', const='clean',
                    help="clean all database collection without usosinstances and course_class_types")
parser.add_argument('-r', '--recreate', action='store_const', dest='option', const='recreate',
                    help="recreate dictionaries - usosinstances")
parser.add_argument('-i', '--index', action='store_const', dest='option', const='index',
                    help="creates indexes on collections")
parser.add_argument('-e', '--environment', action='store', dest='environment',
                    help="environment [development, production, demo] - default development", default='development')
parser.add_argument('-f', '--refresh_failures', action='store_const', dest='option', const='refresh_failures',
                    help="create refresh jobs for users with failure USOS API calls", default='development')
parser.add_argument('-s', '--subscribe', action='store_const', dest='option', const='subscribe',
                    help="create subscribe jobs for all paired users", default='development')


def main():
    args = parser.parse_args()

    config = Config(args.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)
    dbutils = DbUtils(config)

    if args.option == 'recreate':
        logging.info('recreate usosinstances start')
        dbutils.recreate_database(config.AES_SECRET)
        logging.info('recreate usosinstances end')

    elif args.option == 'clean':
        logging.info('clean_database start')
        dbutils.drop_collections([constants.COLLECTION_USOSINSTANCES, constants.COLLECTION_COURSES_CLASSTYPES])
        logging.info('clean_database end')

    elif args.option == 'index':
        logging.info('create_indexes start')
        dbutils.create_indexes()
        logging.info('create_indexes end')

    elif args.option == 'refresh_failures':
        dbutils.refresh_failures()

    elif args.option == 'subscribe':
        dbutils.recall_subscribe()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
