# coding=utf-8

import unittest

from tests.api_tests.api_authorized_tests import ApiCoursesTest
from tests.api_tests.api_open_endpoints_tests import ApiRestTest
from tests.api_tests.files_tests import ApiFilesTest
from tests.api_tests.search_tests import ApiSearchTest
from tests.api_tests.tt_tests import ApiTTTest
from tests.api_tests.user_tests import ApiUserTest
from tests.commons_tests.clamav_tests import ClamAvTest
from tests.commons_tests.config_tests import ConfigTest
from tests.commons_tests.context_tests import ContextTest
from tests.commons_tests.onesignal_tests import OneSignalTest
from tests.commons_tests.usos_caller_tests import UsosCallerTest
from tests.crawler_tests.crawler_tests import CrawlerTest
from tests.event_tests.event_tests import EventTest
from tests.event_tests.event_utils_tests import EventUtilsTest
from tests.scripts_tests.dbutilts_tests import DbUtilsTest


def build_suite():
    test_suite = unittest.TestSuite()

    # api
    test_suite.addTest(unittest.makeSuite(ApiFilesTest))
    test_suite.addTest(unittest.makeSuite(ApiUserTest))
    test_suite.addTest(unittest.makeSuite(ApiCoursesTest))
    test_suite.addTest(unittest.makeSuite(ApiSearchTest))
    test_suite.addTest(unittest.makeSuite(ApiRestTest))
    test_suite.addTest(unittest.makeSuite(ApiTTTest))

    # commons
    test_suite.addTest(unittest.makeSuite(ClamAvTest))
    # test_suite.addTest(unittest.makeSuite(AESCipherTest))
    test_suite.addTest(unittest.makeSuite(UsosCallerTest))
    test_suite.addTest(unittest.makeSuite(ConfigTest))
    test_suite.addTest(unittest.makeSuite(ContextTest))
    test_suite.addTest(unittest.makeSuite(OneSignalTest))

    # crawler
    test_suite.addTest(unittest.makeSuite(CrawlerTest))

    # events
    test_suite.addTest(unittest.makeSuite(EventUtilsTest))
    test_suite.addTest(unittest.makeSuite(EventTest))

    # scripts
    test_suite.addTest(unittest.makeSuite(DbUtilsTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
