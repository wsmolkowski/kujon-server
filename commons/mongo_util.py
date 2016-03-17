import logging
from datetime import datetime
import sys
import traceback
from pprint import pprint

import pymongo
import tornado.gen
import tornado.ioloop

import constants
import settings
import utils
from usosutils.usoscrawler import UsosCrawler

log = logging.getLogger(__name__)

INDEXED_FIELDS = (constants.USOS_ID, constants.USER_ID, constants.COURSE_ID, constants.TERM_ID, constants.ID,
                  constants.UNIT_ID, constants.GROUP_ID, constants.PROGRAMME_ID, constants.FACULTY_ID,
                  constants.USOS_PAIRED)


def get_client():
    return pymongo.Connection(settings.MONGODB_URI)[settings.MONGODB_NAME]


def ensure_indexes():
    db = get_client()
    for collection in db.collection_names():
        if 'system' in collection:
            continue

        for field in INDEXED_FIELDS:
            if db[collection].find_one({field: {'$exists': True, '$ne': False}}):
                index = db[collection].create_index(field)
                logging.info('created index {0} on collection {1} and field {2}'.format(index, collection, field))


def reindex():
    db = get_client()

    for collection in db.collection_names():
        if 'system' in collection:
            continue
        ri = db[collection].reindex()
        pprint(ri)
        logging.info('collection {0} reindexed'.format(collection))


def convert_bytes(bytes):
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


def print_statistics():
    db = get_client()

    print
    print '#' * 25 + ' gathering statistics ' + '#' * 25
    print

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

        print
        print '#' * 25 + ' collection {0} '.format(collection) + '#' * 25
        print
        pprint(stats, width=1)

        summary["count"] += stats["count"]
        summary["size"] += stats["size"]
        summary["indexSize"] += stats.get("totalIndexSize", 0)
        summary["storageSize"] += stats.get("storageSize", 0)

    print
    print '#' * 25 + ' statistics ' + '#' * 25
    print
    print "Total Documents:", summary["count"]
    print "Total Data Size:", convert_bytes(summary["size"])
    print "Total Index Size:", convert_bytes(summary["indexSize"])
    print "Total Storage Size:", convert_bytes(summary["storageSize"])

    print
    print '#' * 25 + '#' * 25
    print


def save_statistics():
    db = get_client()

    db_stats = db.command("dbstats")
    db_stats[constants.CREATED_TIME] = datetime.now()
    pprint(db_stats)

    sh_doc = db[constants.COLLECTION_STATISTICS_HISTORY].insert(db_stats)

    logging.info('saved database statistics in collection {0} with id {1}'.format(
        constants.COLLECTION_STATISTICS_HISTORY, sh_doc))


@tornado.gen.coroutine
def clean_database():
    uc = UsosCrawler()

    try:
        uc.drop_collections()
        uc.recreate_usos()
        yield uc.recreate_dictionaries()
    except Exception, ex:
        print "Problem during database cleanup: {0}".format(ex.message)
        traceback.print_exc()
        sys.exit(-1)


def clean():
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.run_sync(clean_database)


if __name__ == "__main__":
    utils.initialize_logging('mongo_utils')

    # clean()
    # ensure_indexes()
    # reindex()
    # print_statistics()
    # save_statistics()
