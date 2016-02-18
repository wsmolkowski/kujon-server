import unittest

from usoscrowler_tests import CrowlerTest
from usosclient_tests import ClientTest
from usosasync_tests import UsosAsyncTest
from serialize_tests import SerializationTest


def build_suite():

    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(CrowlerTest))
    test_suite.addTest(unittest.makeSuite(ClientTest))
    test_suite.addTest(unittest.makeSuite(UsosAsyncTest))
    test_suite.addTest(unittest.makeSuite(SerializationTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
