import unittest

from handlers_api_courses_tests import ApiCoursesTest
from handlers_api_grades_tests import ApiGradesTest
from handlers_api_user_tests import ApiUserTest
from handlers_api_terms_tests import ApiTermsTest
from usoscrowler_tests import CrowlerTest
from usosclient_tests import ClientTest
from usosasync_tests import UsosAsyncTest


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
