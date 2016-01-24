import unittest

from handlers_api_courses_tests import ApiCoursesTest
from handlers_api_grades_tests import ApiGradesTest
from handlers_api_user_tests import ApiUserTest
from tests_base import TestHelloApp


def build_suite():

    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(TestHelloApp))
    test_suite.addTest(unittest.makeSuite(ApiUserTest))
    test_suite.addTest(unittest.makeSuite(ApiCoursesTest))
    test_suite.addTest(unittest.makeSuite(ApiGradesTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
