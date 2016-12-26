# coding=utf-8

import unittest

from tests.api_tests.courses_tests import ApiCoursesTest
from tests.api_tests.rest_tests import ApiRestTest
from tests.api_tests.search_tests import ApiSearchTest
from tests.api_tests.tt_tests import ApiTTTest
from tests.api_tests.user_tests import ApiUserTest
from tests.clamav_tests.clamav_tests import ClamAvTest
from tests.commons_tests.config_tests import ConfigTest
from tests.crawler_tests.crawler_tests import CrawlerTest
from tests.scripts_tests.dbutilts_tests import DbUtilsTest


def build_suite():
    test_suite = unittest.TestSuite()

    # clamav tests
    test_suite.addTest(unittest.makeSuite(ClamAvTest))

    # api
    test_suite.addTest(unittest.makeSuite(ApiUserTest))
    test_suite.addTest(unittest.makeSuite(ApiCoursesTest))
    test_suite.addTest(unittest.makeSuite(ApiSearchTest))
    test_suite.addTest(unittest.makeSuite(ApiRestTest))
    test_suite.addTest(unittest.makeSuite(ApiTTTest))

    # commons
    # test_suite.addTest(unittest.makeSuite(SerializationTest))
    # test_suite.addTest(unittest.makeSuite(AESCipher))
    test_suite.addTest(unittest.makeSuite(ConfigTest))

    # crawler
    test_suite.addTest(unittest.makeSuite(CrawlerTest))

    # scripts
    test_suite.addTest(unittest.makeSuite(DbUtilsTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
