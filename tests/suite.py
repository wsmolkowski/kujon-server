# coding=utf-8

import unittest

from tests.api_tests.courses_tests import ApiCoursesTest
from tests.api_tests.rest_tests import ApiRestTest
from tests.api_tests.search_tests import ApiSearchTest
from tests.api_tests.user_tests import ApiUserTest
from tests.crawler_tests.crawler_tests import CrawlerTest


def build_suite():
    test_suite = unittest.TestSuite()

    # api
    test_suite.addTest(unittest.makeSuite(ApiUserTest))
    test_suite.addTest(unittest.makeSuite(ApiCoursesTest))
    test_suite.addTest(unittest.makeSuite(ApiSearchTest))
    test_suite.addTest(unittest.makeSuite(ApiRestTest))

    # commons
    # test_suite.addTest(unittest.makeSuite(SerializationTest))
    # test_suite.addTest(unittest.makeSuite(AESCipher))

    # crawler
    test_suite.addTest(unittest.makeSuite(CrawlerTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
