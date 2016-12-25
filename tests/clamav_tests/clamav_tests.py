# coding=utf-8

import unittest

import pyclamd

from commons.config import Config
from commons.enumerators import Environment


class ClamAvTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.config = Config(Environment.TESTS.value)
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConnectClamv(self):
        # assume
        self.config = Config(Environment.TESTS.value)

        cd = pyclamd.ClamdNetworkSocket()

        # when
        result = cd.version().split()[0]

        # then
        self.assertEqual(result, "ClamAV")

    def testContainsEicar(self):
        # assume
        cd = pyclamd.ClamdNetworkSocket()

        # when
        result = cd.scan_stream(bytes(self.config.CLAM_EICAR_SIGNATURE, 'utf-8'))

        # then
        self.assertIsNotNone(result)
        self.assertEqual(result['stream'], ('FOUND', 'Eicar-Test-Signature'))

    def testNotContainsEicar(self):
        # assume
        cd = pyclamd.ClamdNetworkSocket()

        # when
        result = cd.scan_stream(bytes(self.config.CLAM_EICAR_FALSE_SIGNATURE, 'utf-8'))

        # then
        self.assertIsNone(result)


