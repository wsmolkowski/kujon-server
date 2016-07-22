# coding=utf-8
import unittest

from aescipher_tests import AESCipher
from serialize_tests import SerializationTest


def build_suite():

    test_suite = unittest.TestSuite()

    # test_suite.addTest(unittest.makeSuite(CrawlerTest))
    # test_suite.addTest(unittest.makeSuite(ClientTest))
    # test_suite.addTest(unittest.makeSuite(UsosAsyncTest))
    test_suite.addTest(unittest.makeSuite(SerializationTest))
    test_suite.addTest(unittest.makeSuite(AESCipher))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
