import unittest

from staracommon.tests.usosasync_tests import UsosAsyncTest


def build_suite():

    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(CrowlerTest))
    test_suite.addTest(unittest.makeSuite(ClientTest))
    test_suite.addTest(unittest.makeSuite(UsosAsyncTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
