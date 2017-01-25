# coding=utf-8

from tornado.testing import gen_test

from commons.OneSignal import OneSignal
from commons.config import Config
from commons.enumerators import Environment
from tests.api_tests.base import AbstractApplicationTestBase


class OneSignalTest(AbstractApplicationTestBase):
    def setUp(self):
        super(OneSignalTest, self).setUp()
        self.config = Config(Environment.TESTS.value)

    @gen_test(timeout=10)
    def testOneSignalMessageSend(self):
        # assume
        osm = OneSignal(self.config)

        # when
        result = yield osm.signal_message(message="test message from unit tests.",
                                          email_reciepient="wojciech.smolkowski@gmail.com")

        # then
        self.assertIsNotNone(result)
