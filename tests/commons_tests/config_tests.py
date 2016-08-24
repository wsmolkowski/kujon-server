import unittest

from commons.config import Config
from commons.enumerators import Environment


class ConfigTest(unittest.TestCase):
    def testConfig(self):
        self.assertIsNotNone(Config('tests'))
        self.assertIsNotNone(Config(Environment.TESTS.value))
        self.assertIsNotNone(Config(Environment.TESTS))
