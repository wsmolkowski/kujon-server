# coding=utf-8

from tornado.testing import gen_test

from commons.config import Config
from commons.enumerators import Environment
from commons.mixins.OneSignalMixin import OneSignalMixin
from tests.api_tests.base import AbstractApplicationTestBase


class OneSignalMixinTest(AbstractApplicationTestBase):
    def setUp(self):
        super(OneSignalMixinTest, self).setUp()
        self.config = Config(Environment.TESTS.value)

    @gen_test(timeout=30)
    def testOneSignalMessageSend(self):
        # assume
        osm = OneSignalMixin(self.config)

        # when
        result = yield osm.signal_message(message="test message",
                                          email_reciepient="wojciech.smolkowski@gmail.com")

        # then
        self.assertIsNotNone(result)
