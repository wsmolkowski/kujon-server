# coding=utf-8

import logging

from tornado.log import enable_pretty_logging
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from commons.config import Config
from commons.context import Context
from commons.enumerators import Environment
from tests.base import USER_DOC, USOS_DEMO

enable_pretty_logging()
logging.getLogger().setLevel(logging.DEBUG)


class ContextTest(AsyncHTTPTestCase):
    def get_app(self):
        return None

    @gen_test(timeout=10)
    def testContext(self):
        # assume
        config = Config(Environment.TESTS.value)
        context = Context(config=config, user_doc=USER_DOC, usos_doc=USOS_DEMO, refresh=True)

        # when
        result = yield context.asyncCaller.call_async(path='services/courses/classtypes_index')

        # then
        self.assertIsNotNone(result)
