#!/usr/bin/python3
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


def clean(skip_collection=None):
    if not skip_collection:
        skip_collection = []
        
    logging.info('clean_database start')
    mongo_util.drop_collections(skip_collection)
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

parser.add_argument('-c', '--clean', action='store_const', dest='option', const='clean',
                    help="clean all database collection without usosinstances and course_class_types")
parser.add_argument('-ca', '--cleanall', action='store_const', dest='option', const='cleanall',
                    help="clean all database collection")
parser.add_argument('-r', '--recreate', action='store_const', dest='option', const='recreate',
                    help="recreate dictionaries")
parser.add_argument('-i', '--index', action='store_const', dest='option', const='index',
                    help="creates indexes on collections")
parser.add_argument('-s', '--statistics', action='store_const', dest='option', const='statistics',
                    help="creates indexes on collections")


def main():

    args = parser.parse_args()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.INFO)

    if args.option == 'recreate':
        drop()
        recreate()
    elif args.option == 'clean':
        clean([constants.COLLECTION_USOSINSTANCES, constants.COLLECTION_COURSES_CLASSTYPES])
    elif args.option == 'cleanall':
        clean()
    elif args.option == 'index':
        index()
    elif args.option == 'statistics':
        statistics()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
