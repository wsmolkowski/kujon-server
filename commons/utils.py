import os
import sys
import logging
import tempfile
import httplib2
import datetime
import traceback
from bson.objectid import ObjectId

try:
    import socks
except:
    from httplib2 import socks

import settings
import constants

LOGGING_MAX_BYTES = 5 * 1024 * 1024
LOG = logging.getLogger(__name__)


def get_proxy():
    if settings.PROXY_PORT and settings.PROXY_URL:
        return httplib2.ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host=settings.PROXY_URL, proxy_port=settings.PROXY_PORT, proxy_rdns=False)
    return None


def serialize_dictionary(data):
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = serialize_list(value)
        elif isinstance(value, dict):
            data[key] = serialize_dictionary(value)
        elif isinstance(value, datetime.datetime):
            data[key] = value.strftime(constants.DATETIME_DISPLAY_FORMAT)
        elif isinstance(value, ObjectId):
            data.pop(key)
    return data


def serialize_list(data):
    result = []
    for element in data:
        if isinstance(element, list):
            result.append(serialize_list(element))
        elif isinstance(element, dict):
            result.append(serialize_dictionary(element))
        elif isinstance(element, datetime.datetime):
            result.append(element.strftime(constants.DATETIME_DISPLAY_FORMAT))
        elif isinstance(element, ObjectId):
            continue
        else:
            result.append(element)
    return result


def serialize(data):
    if isinstance(data, list):
        return serialize_list(data)
    elif isinstance(data, dict):
        return serialize_dictionary(data)

    return data


def mkdir(newdir):

    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                    "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(newdir)


def initialize_logging(logger_name):

    try:
        log_format = '%%(asctime)s | %%(levelname)s | %s | %%(name)s(%%(filename)s:%%(lineno)s) | %%(message)s' % logger_name
        log_date_format = "%Y-%m-%d %H:%M:%S"

        logging.basicConfig(
            format=log_format,
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
        )

        # set up file loggers
        log_dir = os.path.join(tempfile.gettempdir(), settings.PROJECT_TITLE).lower()
        if not os.path.exists(log_dir):
            mkdir(log_dir)

        log_file = os.path.join(log_dir, '{0}.log'.format(logger_name))

        file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=LOGGING_MAX_BYTES, backupCount=1)
        formatter = logging.Formatter(log_format, log_date_format)
        file_handler.setFormatter(formatter)

        root_log = logging.getLogger()
        root_log.addHandler(file_handler)

        logging.debug("DEBUG MODE is ON")

    except Exception as e:
        sys.stderr.write("Couldn't initialize logging: %s\n" % str(e))
        traceback.print_exc()

        # if config fails entirely, enable basic stdout logging as a fallback
        logging.basicConfig(
            format=log_format,
            level=logging.INFO,
        )

    # re-get the log after logging is initialized
    global LOG
    LOG = logging.getLogger(__name__)