# coding=UTF-8

import logging
import os
import sys
import tempfile
import traceback
from logging import handlers

import certifi
from tornado import httpclient
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders

try:
    import socks
except ImportError:
    from httplib2 import socks

from commons import constants

LOGGING_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_FORMAT = '%%(asctime)s %%(levelname)s %s %%(module)s:%%(lineno)s %%(message)s'

log = logging.getLogger(__name__)


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


def initialize_logging(logger_name, log_level='DEBUG', log_dir=None, ):
    log_format = DEFAULT_FORMAT % logger_name

    try:
        logging.basicConfig(
            format=log_format,
            level=log_level,
        )

        # set up file loggers
        if not log_dir:
            log_dir = os.path.join(tempfile.gettempdir(), 'kujon.mobi')
        else:
            log_dir = log_dir

        if not os.path.exists(log_dir):
            mkdir(log_dir)

        log_file = os.path.join(log_dir, '{0}.log'.format(logger_name))

        file_handler = handlers.RotatingFileHandler(log_file, maxBytes=LOGGING_MAX_BYTES, backupCount=1)
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


def http_client(proxy_url=None, proxy_port=None):
    httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                         defaults=dict(proxy_host=proxy_url,
                                                       proxy_port=proxy_port,
                                                       validate_cert=constants.HTTP_VALIDATE_CERT,
                                                       ca_certs=certifi.where()),
                                         max_clients=constants.MAX_HTTP_CLIENTS)

    return httpclient.AsyncHTTPClient()


def http_request(url, proxy_url=None, proxy_port=None, decompress_response=True, headers=None, x_forwarded_for=None,
                 prepare_curl_callback=None):
    if not headers:
        headers = HTTPHeaders({})

    headers.add('application/json', 'application/json')
    if x_forwarded_for:
        headers.add('X-Forwarded-For', x_forwarded_for)

    return HTTPRequest(url=url,
                       decompress_response=decompress_response,
                       headers=headers,
                       prepare_curl_callback=prepare_curl_callback,
                       proxy_host=proxy_url,
                       proxy_port=proxy_port,
                       connect_timeout=constants.HTTP_CONNECT_TIMEOUT,
                       request_timeout=constants.HTTP_REQUEST_TIMEOUT)
