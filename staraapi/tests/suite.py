import unittest

from usosclient_tests import ClientTest
from usoscrowler_tests import CrowlerTest

from staracommon.tests.usosasync_tests import UsosAsyncTest


def build_suite():

    test_suite = unittest.TestSuite()

    #test_suite.addTest(unittest.makeSuite(ApiUserTest))
    #test_suite.addTest(unittest.makeSuite(ApiCoursesTest))
    #test_suite.addTest(unittest.makeSuite(ApiGradesTest))
    #test_suite.addTest(unittest.makeSuite(ApiTermsTest))
    test_suite.addTest(unittest.makeSuite(CrowlerTest))
    test_suite.addTest(unittest.makeSuite(ClientTest))
    test_suite.addTest(unittest.makeSuite(UsosAsyncTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
