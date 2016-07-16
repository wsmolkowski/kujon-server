# coding=UTF-8

import logging
import os
import sys
import tempfile
import traceback

from tornado import httpclient

try:
    import socks
except ImportError:
    from httplib2 import socks

from commons import settings
from commons import constants

LOGGING_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_FORMAT = '%%(asctime)s %%(levelname)s %s %%(module)s:%%(lineno)s %%(message)s'

log = logging.getLogger(__name__)


# def get_proxy():
#     if settings.PROXY_PORT and settings.PROXY_URL:
#         return httplib2.ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host=settings.PROXY_URL,
#                                   proxy_port=settings.PROXY_PORT, proxy_rdns=False)
#     return None


def mkdir(newdir):
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(newdir)


def initialize_logging(logger_name):
    log_format = DEFAULT_FORMAT % logger_name

    try:
        logging.basicConfig(
            format=log_format,
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
        )

        # set up file loggers
        if not settings.LOG_DIR:
            log_dir = os.path.join(tempfile.gettempdir(), settings.PROJECT_TITLE)
        else:
            log_dir = settings.LOG_DIR

        if not os.path.exists(log_dir):
            mkdir(log_dir)

        log_file = os.path.join(log_dir, '{0}.log'.format(logger_name))

        file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=LOGGING_MAX_BYTES, backupCount=1)
        formatter = logging.Formatter(log_format, constants.DEFAULT_DATE_FORMAT)
        file_handler.setFormatter(formatter)

        root_log = logging.getLogger()
        root_log.addHandler(file_handler)

    except Exception as e:
        sys.stderr.write("Couldn't initialize logging: %s\n" % str(e))
        traceback.print_exc()

        # if config fails entirely, enable basic stdout logging as a fallback
        logging.basicConfig(format=log_format, level=logging.INFO, )

    # re-get the log after logging is initialized
    global log
    log = logging.getLogger(__name__)


def http_client():
    if settings.PROXY_URL and settings.PROXY_PORT:
        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                             defaults=dict(proxy_host=settings.PROXY_URL,
                                                           proxy_port=settings.PROXY_PORT,
                                                           validate_cert=False),
                                             max_clients=constants.MAX_HTTP_CLIENTS)

    else:
        httpclient.AsyncHTTPClient.configure(None, max_clients=constants.MAX_HTTP_CLIENTS)

    return httpclient.AsyncHTTPClient()
