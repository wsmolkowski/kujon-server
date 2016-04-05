import argparse
import logging
import sys

import tornado.gen
import tornado.ioloop

from commons import settings, constants, utils, mongo_util

utils.initialize_logging('dbutils')


def drop():
    logging.info('drop_collections start')
    mongo_util.drop_collections()
    logging.info('drop_collections end')


def clean():
    logging.info('clean_database start')
    mongo_util.drop_collections([constants.COLLECTION_USERS, ])
    logging.info('clean_database end')


def recreate():
    logging.info('recreate_database start')
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.run_sync(mongo_util.recreate_database)
    logging.info('recreate_database end')


def create_user_jobs():
    logging.info('create_user_jobs start')
    mongo_util.create_user_jobs()
    logging.info('create_user_jobs end')


def index():
    logging.info('create_indexes start')
    mongo_util.create_indexes()
    logging.info('create_indexes end')


def statistics():
    mongo_util.print_statistics()


parser = argparse.ArgumentParser(
    description="performs a variety of operations on a file.",
    epilog="pretty neat, huh?",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument('-d', '--drop', action='store_const', dest='option', const='drop',
                    help="drop all database collection")
parser.add_argument('-r', '--recreate', action='store_const', dest='option', const='recreate',
                    help="recreate dictionaries")
parser.add_argument('-i', '--index', action='store_const', dest='option', const='index',
                    help="creates indexes on collections")
parser.add_argument('-s', '--statistics', action='store_const', dest='option', const='statistics',
                    help="creates indexes on collections")


def main():
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    args = parser.parse_args()

    if args.option == 'drop':
        drop()
    elif args.option == 'recreate':
        clean()
        recreate()
        create_user_jobs()
    elif args.option == 'index':
        index()
    elif args.option == 'statistics':
        statistics()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
