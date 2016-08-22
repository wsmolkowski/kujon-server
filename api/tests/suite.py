# coding=utf-8

import unittest

from api.tests.api_rest_tests import ApiTest


def build_suite():
    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(ApiTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
