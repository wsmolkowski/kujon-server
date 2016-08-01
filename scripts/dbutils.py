# coding=UTF-8

import argparse
import logging
import sys

import pymongo
from bson.objectid import ObjectId
from commons import constants, usosinstances, utils
from commons.AESCipher import AESCipher
from commons.config import Config

utils.initialize_logging('dbutils')


class DbUtils(object):
    INDEXED_FIELDS = (constants.USOS_ID, constants.USER_ID, constants.COURSE_ID, constants.TERM_ID, constants.ID,
                      constants.UNIT_ID, constants.GROUP_ID, constants.PROGRAMME_ID, constants.FACULTY_ID,
                      constants.USOS_PAIRED, constants.USER_EMAIL, constants.NODE_ID)

    def __init__(self, config, encrypt_usoses_keys=False):
        self.config = config
        self.encrypt_usoses_keys = encrypt_usoses_keys
        self.client = pymongo.Connection(self.config.MONGODB_URI)[self.config.MONGODB_NAME]

    def _ttl_index(self, collection, field):
        ttl_index = self.client[constants.COLLECTION_TOKENS].create_index(field,
                                                                          expireAfterSeconds=constants.TOKEN_EXPIRATION_TIMEOUT)
        logging.info('created ttl index {0} on collection {1} and field {2}'.format(ttl_index, collection, field))

    def _unique_index(self, collection, fields):
        index = self.client[collection].create_index(fields, unique=True, drop_dups=True)

        logging.info('unique index: {0} created on collection: {1} and fields {2}'.format(
            index, collection, fields))

    def _unique_indexes(self):
        # create_unique_index(constants.COLLECTION_USERS_INFO,
        #                     [(constants.USOS_ID, pymongo.ASCENDING), (constants.ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_TERMS,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.TERM_ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_FACULTIES,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.FACULTY_ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_PROGRAMMES,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.PROGRAMME_ID, pymongo.ASCENDING)])
        self._unique_index(constants.COLLECTION_COURSES,
                           [(constants.USOS_ID, pymongo.ASCENDING), (constants.COURSE_ID, pymongo.ASCENDING)])

    def create_indexes(self):
        for collection in self.client.collection_names(include_system_collections=False):
            for field in self.INDEXED_FIELDS:
                if self.client[collection].find_one({field: {'$exists': True, '$ne': False}}):
                    index = self.client[collection].create_index(field)
                    logging.info('created index {0} on collection {1} and field {2}'.format(index, collection, field))

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

        # def create_user_jobs(self):
        #     for user_doc in self.client[constants.COLLECTION_USERS].find():
        #         logging.info('creating initial job for user {0}'.format(user_doc[constants.MONGO_ID]))
        #         self.client[constants.COLLECTION_JOBS_QUEUE].insert(
        #             job_factory.initial_user_job(user_doc[constants.MONGO_ID]))

    def copy_user_crediteltials(self, email_from, email_to):

        try:

            user_from_doc = self.client[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email_from})
            if not user_from_doc:
                logging.error("user from %r not found.", email_from)
                return None

            user_from_info_doc = self.client[constants.COLLECTION_USERS_INFO].find_one(
                {constants.USER_ID: user_from_doc[constants.MONGO_ID]})
            if not user_from_info_doc:
                logging.error("user_info from  %r or %r not found ", email_from)
                return None

            user_to_doc = self.client[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email_to})
            if not user_from_doc:
                logging.error("user to %r not found.", email_to)
                return None

            user_to_info_doc = self.client[constants.COLLECTION_USERS_INFO].find_one(
                {constants.USER_ID: ObjectId(user_to_doc[constants.MONGO_ID])})
            if not user_from_info_doc:
                logging.error("user_info to  %r or %r not found ", email_to)
                return None

            document = user_to_info_doc
            document[constants.USER_ID] = ObjectId(user_from_doc[constants.MONGO_ID])
            update_doc = self.db_update(constants.COLLECTION_USERS_INFO, document[constants.MONGO_ID], document)


            return None
        except Exception as ex:
            print(ex.messg)

        pass

        return None

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
parser.add_argument('-f', '--fakeuser', nargs=2, action='store', dest='user',
                    help="copy credentials from user1 to user2")



def main():
    args = parser.parse_args()

    config = Config(args.environment)
    logging.getLogger().setLevel(config.LOG_LEVEL)
    dbutils = DbUtils(config)

    logging.getLogger().setLevel(config.LOG_LEVEL)

    if args.user and len(args.user) == 2:
        logging.info('coping creditentials from users1 to user2 (by email)')
        dbutils.copy_user_crediteltials(args.user[0], args.user[1])
        logging.info('done.')

    elif args.option == 'recreate':
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
