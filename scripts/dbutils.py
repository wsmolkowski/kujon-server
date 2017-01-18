# coding=UTF-8

import argparse
import logging
import sys
from datetime import datetime

import pymongo

from commons import usosinstances, utils
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.constants import config as constants_config
from commons.constants import fields, collections
from commons.enumerators import Environment
from commons.enumerators import ExceptionTypes
from crawler import job_factory


class DbUtils(object):
    INDEXED_FIELDS = (fields.USOS_ID, fields.USER_ID, fields.COURSE_ID, fields.TERM_ID, fields.ID,
                      fields.UNIT_ID, fields.GROUP_ID, fields.PROGRAMME_ID, fields.FACULTY_ID,
                      fields.USOS_PAIRED, fields.USER_EMAIL, fields.NODE_ID, fields.FILE_STATUS)

    def __init__(self, config, encrypt_usoses_keys=False):
        if config:
            self.config = config
            self.encrypt_usoses_keys = encrypt_usoses_keys
            self.client = pymongo.MongoClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]

            utils.initialize_logging('dbutils', log_dir=self.config.LOG_DIR)
            logging.info(self.client)

    def _ttl_index(self, collection, field, after_seconds):
        try:
            ttl_index = self.client[collections.TOKENS].create_index(field, expireAfterSeconds=after_seconds)
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
        self._unique_index(collections.USERS_INFO,
                           [(fields.USOS_ID, pymongo.ASCENDING), (fields.ID, pymongo.ASCENDING)])
        self._unique_index(collections.TERMS,
                           [(fields.USOS_ID, pymongo.ASCENDING), (fields.TERM_ID, pymongo.ASCENDING)])
        self._unique_index(collections.FACULTIES,
                           [(fields.USOS_ID, pymongo.ASCENDING), (fields.FACULTY_ID, pymongo.ASCENDING)])
        self._unique_index(collections.PROGRAMMES,
                           [(fields.USOS_ID, pymongo.ASCENDING), (fields.PROGRAMME_ID, pymongo.ASCENDING)])
        self._unique_index(collections.COURSES,
                           [(fields.USOS_ID, pymongo.ASCENDING), (fields.COURSE_ID, pymongo.ASCENDING)])
        self._unique_index(collections.COURSES_EDITIONS, [(fields.USER_ID, pymongo.ASCENDING)])

        self.client[collections.COURSES_CLASSTYPES].create_index(fields.USOS_ID, unique=True)

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

        self._ttl_index(collections.TOKENS, fields.CREATED_TIME, constants_config.SECONDS_HOUR)
        self._ttl_index(collections.COURSES_CLASSTYPES, fields.CREATED_TIME, constants_config.SECONDS_DAY)
        self._ttl_index(collections.EVENTS_VERIFY_TOKENS, fields.CREATED_TIME, 120)

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
            self.client.drop_collection(collections.USOSINSTANCES)
            msg = "Added usos to instances: "
            for usos in usosinstances.USOSINSTANCES:
                usos[fields.CREATED_TIME] = now
                doc = self.client.usosinstances.find_one({fields.USOS_ID: usos[fields.USOS_ID]})
                if not doc:
                    if self.encrypt_usoses_keys:
                        self.client[collections.USOSINSTANCES].insert(aes.encrypt_usos(usos))
                    else:
                        self.client[collections.USOSINSTANCES].insert(usos)
                msg = msg + usos[fields.USOS_ID] + " "
            logging.debug(msg)

        except Exception as ex:
            logging.exception(ex)

    def remove_user_data(self, user_id, client=False):
        if not client:
            client = self.db

        for collection in client.collection_names(include_system_collections=False):
            if collection in (collections.USERS,):
                continue

            exists = client[collection].find_one({fields.USER_ID: {'$exists': True, '$ne': False}})
            if exists:
                client[collection].remove({fields.USER_ID: user_id})

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

            user_from_doc = self.db_from[collections.USERS].find_one({
                fields.USER_EMAIL: email_from, fields.USOS_PAIRED: True})
            if not user_from_doc:
                raise Exception("user from {0} not found.".format(email_from))

            logging.info('user_from_doc: {0}'.format(user_from_doc))

            user_to_doc = self.db_to[collections.USERS].find_one({
                fields.USER_EMAIL: email_to, fields.USOS_PAIRED: True})
            if not user_to_doc:
                raise Exception("user to {0} not found.".format(email_to))

            logging.info('user_to_doc: {0}'.format(user_to_doc))

            self.remove_user_data(user_to_doc[fields.MONGO_ID], self.db_to)
            logging.info('removed user to data')

            user_to_doc[fields.ACCESS_TOKEN_KEY] = user_from_doc[fields.ACCESS_TOKEN_KEY]
            user_to_doc[fields.ACCESS_TOKEN_SECRET] = user_from_doc[fields.ACCESS_TOKEN_SECRET]
            user_to_doc[fields.USOS_ID] = user_from_doc[fields.USOS_ID]

            if fields.USOS_USER_ID in user_from_doc:
                user_to_doc[fields.USOS_USER_ID] = user_from_doc[fields.USOS_USER_ID]

            updated = self.db_to[collections.USERS].update(
                {fields.MONGO_ID: user_to_doc[fields.MONGO_ID]}, user_to_doc)

            logging.info('collection: {0} updated: {1}'.format(collections.USERS, updated))

            self.db_to[collections.JOBS_QUEUE].insert(
                job_factory.refresh_user_job(user_to_doc[fields.MONGO_ID]))

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
            user_ids = self.client[collections.EXCEPTIONS].find({'exception_type': ExceptionTypes.API.value}) \
                .distinct(fields.USER_ID)

            for user_id in user_ids:
                if not user_id:
                    continue

                user_doc = self.client[collections.USERS].find_one(
                    {fields.MONGO_ID: user_id, fields.USOS_PAIRED: True})
                if not user_doc:
                    continue

                self.client[collections.EXCEPTIONS].remove({fields.USER_ID: user_id})
                logging.info('removed exception data for user_id {0}'.format(user_id))

                self.client[collections.JOBS_QUEUE].insert(job_factory.refresh_user_job(user_id))
                logging.info('created refresh task for user_id {0}'.format(user_id))

        except Exception as ex:
            logging.exception(ex)

    def recall_subscribe(self):
        '''
            for each paired user check if subscription collection is filled otherwise subscribe job is created
        :return:
        '''

        try:
            user_ids = self.client[collections.USERS].find({fields.USOS_PAIRED: True})

            for user_id in user_ids:
                if not user_id:
                    continue

                logging.info('processing: {0}'.format(user_id[fields.MONGO_ID]))

                subsctiption_count = self.client[collections.SUBSCRIPTIONS].find(
                    {fields.USER_ID: user_id[fields.MONGO_ID]}).count()

                if subsctiption_count == 3:  # 'crstests/user_grade', 'grades/grade', 'crstests/user_point'
                    continue

                self.client[collections.JOBS_QUEUE].insert(
                    job_factory.subscribe_user_job(user_id[fields.MONGO_ID]))
                logging.info('created subscribe task for user_id {0}'.format(user_id[fields.MONGO_ID]))

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
        dbutils.drop_collections([collections.USOSINSTANCES, collections.COURSES_CLASSTYPES])
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
