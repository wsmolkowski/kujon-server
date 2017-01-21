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
from tornado.log import LogFormatter

from commons.constants import config

try:
    import socks
except ImportError:
    from httplib2 import socks

LOGGING_MAX_BYTES = 5 * 1024 * 1024
LOGGING_MAX_BACUP = 10

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


def initialize_logging(logger_name, log_level=None, log_dir=None):
    if not log_level:
        log_level = logging.DEBUG

    try:
        # set up file loggers
        if not log_dir:
            log_dir = os.path.join(tempfile.gettempdir(), 'kujon.mobi')
        else:
            log_dir = log_dir

        if not os.path.exists(log_dir):
            mkdir(log_dir)

        log_file = os.path.join(log_dir, '{0}.log'.format(logger_name))

        file_handler = handlers.RotatingFileHandler(log_file, maxBytes=LOGGING_MAX_BYTES, backupCount=LOGGING_MAX_BACUP)
        file_handler.setFormatter(LogFormatter())

        if os.path.isfile(log_file):
            file_handler.doRollover()

        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(file_handler)

    except Exception as ex:
        sys.stderr.write("Couldn't initialize logging: %s\n" % str(ex))
        traceback.print_exc()

        # if config fails entirely, enable basic stdout logging as a fallback
        logging.basicConfig(format=LogFormatter(), level=logging.INFO)

    # re-get the log after logging is initialized
    global log
    log = logging.getLogger(__name__)


def http_client(proxy_host=None, proxy_port=None, io_loop=None):
    httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient",
                                         defaults=dict(proxy_host=proxy_host,
                                                       proxy_port=proxy_port,
                                                       validate_cert=config.HTTP_VALIDATE_CERT,
                                                       ca_certs=certifi.where()),
                                         max_clients=config.MAX_HTTP_CLIENTS)

    return httpclient.AsyncHTTPClient(io_loop=io_loop)


def http_request(url, proxy_host=None, proxy_port=None, decompress_response=True, headers=None, x_forwarded_for=None,
                 prepare_curl_callback=None, method='GET', body=None):
    if not headers:
        headers = HTTPHeaders({})

    headers.add('Content-type', 'application/json')
    if x_forwarded_for:
        headers.add('X-Forwarded-For', x_forwarded_for)

    return HTTPRequest(url=url,
                       method=method,
                       body=body,
                       decompress_response=decompress_response,
                       headers=headers,
                       prepare_curl_callback=prepare_curl_callback,
                       proxy_host=proxy_host,
                       proxy_port=proxy_port,
                       connect_timeout=config.HTTP_CONNECT_TIMEOUT,
                       request_timeout=config.HTTP_REQUEST_TIMEOUT)
