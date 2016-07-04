# coding=UTF-8

import logging
from datetime import datetime
from pprint import pprint

import pymongo
from tornado import escape
from tornado import gen
from tornado.httpclient import HTTPRequest

from commons import constants, settings, utils, usosinstances
from commons.AESCipher import AESCipher
from crawler import job_factory

INDEXED_FIELDS = (constants.USOS_ID, constants.USER_ID, constants.COURSE_ID, constants.TERM_ID, constants.ID,
                  constants.UNIT_ID, constants.GROUP_ID, constants.PROGRAMME_ID, constants.FACULTY_ID,
                  constants.USOS_PAIRED, constants.USER_EMAIL)


def get_client():
    return pymongo.Connection(settings.MONGODB_URI)[settings.MONGODB_NAME]


def create_indexes():
    db = get_client()
    for collection in db.collection_names(include_system_collections=False):
        for field in INDEXED_FIELDS:
            if db[collection].find_one({field: {'$exists': True, '$ne': False}}):
                index = db[collection].create_index(field)
                logging.info('created index {0} on collection {1} and field {2}'.format(index, collection, field))


def reindex():
    db = get_client()

    for collection in db.collection_names(include_system_collections=False):
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

    print ('#' * 25 + ' gathering statistics ' + '#' * 25)

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

        print ('#' * 25 + ' collection {0} '.format(collection) + '#' * 25)
        pprint(stats, width=1)

        summary["count"] += stats["count"]
        summary["size"] += stats["size"]
        summary["indexSize"] += stats.get("totalIndexSize", 0)
        summary["storageSize"] += stats.get("storageSize", 0)

    print ('#' * 25 + ' statistics ' + '#' * 25)
    print ("Total Documents:", summary["count"])
    print ("Total Data Size:", convert_bytes(summary["size"]))
    print ("Total Index Size:", convert_bytes(summary["indexSize"]))
    print ("Total Storage Size:", convert_bytes(summary["storageSize"]))

    print ('#' * 25 + '#' * 25)


def save_statistics():
    db = get_client()

    db_stats = db.command("dbstats")
    db_stats[constants.CREATED_TIME] = datetime.now()
    pprint(db_stats)

    sh_doc = db[constants.COLLECTION_STATISTICS_HISTORY].insert(db_stats)

    logging.info('saved database statistics in collection {0} with id {1}'.format(
        constants.COLLECTION_STATISTICS_HISTORY, sh_doc))


def drop_collections(skip_collections=[]):
    db = get_client()

    for collection in db.collection_names():
        if 'system' in collection:
            continue
        if collection in skip_collections:
            logging.info('skipping collection: {0}'.format(collection))
            continue
        db.drop_collection(collection)


@gen.coroutine
def _do_recreate(db, usos_doc):
    url = None
    try:
        url = usos_doc[constants.USOS_URL] + 'services/courses/classtypes_index'
        validate_cert = usos_doc[constants.VALIDATE_SSL_CERT]
        http_client = utils.http_client()

        request = HTTPRequest(url=url, method='GET', validate_cert=validate_cert)
        response = yield http_client.fetch(request)

        if response.code is not 200 and response.reason != 'OK':
            logging.error('Błedna odpowiedź USOS dla {0}'.format(url))
            logging.error(response)
            raise gen.Return(None)

        class_types = escape.json_decode(response.body)

        if class_types and len(class_types) > 0:
            class_type_list = list()
            for class_type in class_types.values():
                class_type[constants.USOS_ID] = usos_doc[constants.USOS_ID]
                class_type[constants.CREATED_TIME] = datetime.now()
                class_type_list.append(class_type)
            db[constants.COLLECTION_COURSES_CLASSTYPES].insert(class_type_list)
            logging.info("dictionary course classtypes for usos {0} inserted.".format(usos_doc[constants.USOS_ID]))
        else:
            logging.error("empty dictionaries {0} for {1}".format(constants.COLLECTION_COURSES_CLASSTYPES,
                                                                  usos_doc[constants.USOS_ID]))

    except Exception as ex:
        logging.error("failed to recreate_dictionaries for {0} {1} {2}".format(
            usos_doc[constants.USOS_ID], url, ex.message))
        logging.exception(ex)
    gen.Return(None)


@gen.coroutine
def recreate_dictionaries():
    db = get_client()

    tasks = list()
    db.drop_collection(constants.COLLECTION_COURSES_CLASSTYPES)
    for usos in db[constants.COLLECTION_USOSINSTANCES].find():
        tasks.append(_do_recreate(db, usos))

    yield tasks

    raise gen.Return(True)


def recreate_usos():
    aes = AESCipher()
    db = get_client()
    db.drop_collection(constants.COLLECTION_USOSINSTANCES)
    for usos in usosinstances.USOSINSTANCES:
        logging.info("adding usos: %r ", usos[constants.USOS_ID])
        doc = db.usosinstances.find_one({constants.USOS_ID: usos[constants.USOS_ID]})
        if not doc:
            if settings.ENCRYPT_USOSES_KEYS:
                db[constants.COLLECTION_USOSINSTANCES].insert(aes.encrypt_usos(usos))
            else:
                db[constants.COLLECTION_USOSINSTANCES].insert(usos)


@gen.coroutine
def recreate_database():
    try:
        recreate_usos()
        yield recreate_dictionaries()
    except Exception as ex:
        msg = "Problem during database recreate: {0}".format(ex.message)
        logging.exception(msg, ex)
        raise gen.Return(False)
    raise gen.Return(True)


def create_user_jobs():
    db = get_client()
    for user_doc in db[constants.COLLECTION_USERS].find():
        logging.info('creating initial job for user {0}'.format(user_doc[constants.MONGO_ID]))
        db[constants.COLLECTION_JOBS_QUEUE].insert(job_factory.initial_user_job(user_doc[constants.MONGO_ID]))
