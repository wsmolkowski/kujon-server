# coding=utf-8

import pyclamd
from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ClamAvTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ClamAvTest, self).setUp()

    def tearDown(self):
        pass

    @gen_test(timeout=1)
    def testConnectClamv(self):
        # assume
        cd = pyclamd.ClamdNetworkSocket()

        # when
        result = cd.version().split()[0]

        # then
        self.assertEqual(result, "ClamAV")

    @gen_test(timeout=1)
    def testClamAVContainsEicar(self):
        # assume
        cd = pyclamd.ClamdNetworkSocket()

        # when
        result = cd.scan_stream(bytes(self.config.CLAM_EICAR_SIGNATURE, 'utf-8'))

        # then
        self.assertIsNotNone(result)
        self.assertEqual(result['stream'], ('FOUND', 'Eicar-Test-Signature'))

    @gen_test(timeout=1)
    def testClamAVNotContainsEicar(self):
        # assume
        cd = pyclamd.ClamdNetworkSocket()

        # when
        result = cd.scan_stream(bytes("TEST", 'utf-8'))

        # then
        self.assertIsNone(result)
