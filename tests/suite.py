import unittest

from base_tests import TestHelloApp
from handlers_tests import ApiUserTest
from ususupdater_tests import UsosupdaterTest


def build_suite():

    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(TestHelloApp))
    test_suite.addTest(unittest.makeSuite(UsosupdaterTest))
    test_suite.addTest(unittest.makeSuite(ApiUserTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
