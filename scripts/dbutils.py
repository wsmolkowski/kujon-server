# coding=UTF-8

import argparse
import logging
import sys

import pymongo

from commons import constants, usosinstances, utils
from commons.AESCipher import AESCipher
from commons.config import Config
from commons.enumerators import Environment

utils.initialize_logging('dbutils')


class DbUtils(object):
    INDEXED_FIELDS = (constants.USOS_ID, constants.USER_ID, constants.COURSE_ID, constants.TERM_ID, constants.ID,
                      constants.UNIT_ID, constants.GROUP_ID, constants.PROGRAMME_ID, constants.FACULTY_ID,
                      constants.USOS_PAIRED, constants.USER_EMAIL, constants.NODE_ID)

    def __init__(self, config, encrypt_usoses_keys=False):
        self.config = config
        self.encrypt_usoses_keys = encrypt_usoses_keys
        self.client = pymongo.Connection(self.config.MONGODB_URI)[self.config.MONGODB_NAME]
        logging.info(self.client)

    def _ttl_index(self, collection, field):
        ttl_index = self.client[constants.COLLECTION_TOKENS].create_index(field,
                                                                          expireAfterSeconds=constants.TOKEN_EXPIRATION_TIMEOUT)
        logging.info('created ttl index {0} on collection {1} and field {2}'.format(ttl_index, collection, field))

    def _unique_index(self, collection, fields):
        try:
            index = self.client[collection].create_index(fields, unique=True, drop_dups=True)

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

        self._ttl_index(constants.COLLECTION_TOKENS, constants.FIELD_TOKEN_EXPIRATION)

        self._unique_indexes()

    def reindex(self):
        for collection in self.client.collection_names(include_system_collections=False):
            ri = self.client[collection].reindex()
            logging.info('collection {0} reindexed: {1}'.format(collection, ri))

    def _convert_bytes(self, bytes):
        bytes = float(bytes)
        magnitude = abs(bytes)
        if magnitude >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fT' % terabytes
        elif magnitude >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fG' % gigabytes
        elif magnitude >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fM' % megabytes
        elif magnitude >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fK' % kilobytes
        else:
            size = '%.2fb' % bytes
        return size

    def print_statistics(self):
        db = self.client

        print('#' * 25 + ' gathering statistics ' + '#' * 25)

        summary = {
            "count": 0,
            "size": 0,
            "indexSize": 0,
            "storageSize": 0
        }

        for collection in db.collection_names():
            if 'system' in collection:
                continue
            stats = db.command('collstats', collection)

            summary["count"] += stats["count"]
            summary["size"] += stats["size"]
            summary["indexSize"] += stats.get("totalIndexSize", 0)
            summary["storageSize"] += stats.get("storageSize", 0)

            print("Collection {0} count: {1} size: {2} index_size: {3} storage_size: {4}".format(
                collection,
                stats["count"],
                self._convert_bytes(stats["size"]),
                self._convert_bytes(stats["totalIndexSize"]),
                self._convert_bytes(stats["storageSize"])))

        print('#' * 25 + ' Total statistics ' + '#' * 25)
        print("Total Documents:", summary["count"])
        print("Total Data Size:", self._convert_bytes(summary["size"]))
        print("Total Index Size:", self._convert_bytes(summary["indexSize"]))
        print("Total Storage Size:", self._convert_bytes(summary["storageSize"]))

        print('#' * 25 + '#' * 25)

    def drop_collections(self, skip_collections=None):
        if not skip_collections:
            skip_collections = list()
        db = self.client

        for collection in db.collection_names():
            if 'system' in collection:
                continue
            if collection in skip_collections:
                logging.info('skipping collection: {0}'.format(collection))
                continue
            db.drop_collection(collection)

    def recreate_database(self, aes_secret):
        try:
            aes = AESCipher(aes_secret)
            self.client.drop_collection(constants.COLLECTION_USOSINSTANCES)
            for usos in usosinstances.USOSINSTANCES:
                logging.debug("adding usos: %r ", usos[constants.USOS_ID])
                doc = self.client.usosinstances.find_one({constants.USOS_ID: usos[constants.USOS_ID]})
                if not doc:
                    if self.encrypt_usoses_keys:
                        self.client[constants.COLLECTION_USOSINSTANCES].insert(aes.encrypt_usos(usos))
                    else:
                        self.client[constants.COLLECTION_USOSINSTANCES].insert(usos)
        except Exception as ex:
            logging.exception(ex)
            return False
        return True

    def copy_user_credentials(self, email_from, email_to, environment_from, environment_to='demo'):

        try:
            if environment_to == Environment.PRODUCTION.value:
                raise Exception('Can not copy values to {0} environment. :('.format(Environment.PRODUCTION.value))

            self.config_from = Config(environment_from)
            self.config_to = Config(environment_to)

            self.client_from = pymongo.Connection(self.config_from.MONGODB_URI)
            self.db_from = self.client_from[self.config_from.MONGODB_NAME]
            self.client_to = pymongo.Connection(self.config_to.MONGODB_URI)
            self.db_to = self.client_to[self.config_to.MONGODB_NAME]

            user_from_doc = self.db_from[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email_from})
            if not user_from_doc:
                raise Exception("user from {0} not found.".format(email_from))

            logging.debug('user_from_doc: {0}'.format(user_from_doc))

            user_to_doc = self.db_to[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email_to})
            if not user_from_doc:
                raise Exception("user to {0} not found.".format(email_to))

            logging.debug('user_to_doc: {0}'.format(user_to_doc))

            user_to_doc[constants.ACCESS_TOKEN_KEY] = user_from_doc[constants.ACCESS_TOKEN_KEY]
            user_to_doc[constants.ACCESS_TOKEN_SECRET] = user_from_doc[constants.ACCESS_TOKEN_SECRET]
            user_to_doc[constants.USOS_ID] = user_from_doc[constants.USOS_ID]
            user_to_doc[constants.USOS_USER_ID] = user_from_doc[constants.USOS_USER_ID]

            updated = self.db_to[constants.COLLECTION_USERS].update(
                {constants.MONGO_ID: user_to_doc[constants.MONGO_ID]}, user_to_doc)

            logging.info('collection: {0} updated: {1}'.format(constants.COLLECTION_USERS, updated))
        except Exception as ex:
            logging.exception(ex)
        finally:
            if self.client_from:
                self.client_from.close()
            if self.client_to:
                self.client_to.close()


##################################################################

parser = argparse.ArgumentParser(
    description="Script for local mongo database manipulation.",
    epilog="pretty neat, huh?",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument('-c', '--clean', action='store_const', dest='option', const='clean',
                    help="clean all database collection without usosinstances and course_class_types")
parser.add_argument('-r', '--recreate', action='store_const', dest='option', const='recreate',
                    help="recreate dictionaries")
parser.add_argument('-i', '--index', action='store_const', dest='option', const='index',
                    help="creates indexes on collections")
parser.add_argument('-s', '--statistics', action='store_const', dest='option', const='statistics',
                    help="creates indexes on collections")
parser.add_argument('-e', '--environment', action='store', dest='environment',
                    help="environment [development, production, demo] - default development", default='development')


def main():
    args = parser.parse_args()

    config = Config(args.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)
    dbutils = DbUtils(config)

    if args.option == 'recreate':
        logging.info('drop_collections start')
        dbutils.drop_collections()
        logging.info('drop_collections end')

        logging.info('recreate_database start')
        dbutils.recreate_database(config.AES_SECRET)
        logging.info('recreate_database end')

    elif args.option == 'clean':
        logging.info('clean_database start')
        dbutils.drop_collections([constants.COLLECTION_USOSINSTANCES, constants.COLLECTION_COURSES_CLASSTYPES])
        logging.info('clean_database end')

    elif args.option == 'index':
        logging.info('create_indexes start')
        dbutils.create_indexes()
        logging.info('create_indexes end')

    elif args.option == 'statistics':
        dbutils.print_statistics()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
