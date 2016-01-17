import unittest

from handlers_coursesgrades_tests import ApiCoursesGradesTest
from handlers_user_tests import ApiUserTest
from handlers_usos_tests import ApiUsosTest
from tests_base import TestHelloApp
from ususupdater_tests import UsosupdaterTest


def build_suite():

    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(ApiUsosTest))
    test_suite.addTest(unittest.makeSuite(TestHelloApp))
    test_suite.addTest(unittest.makeSuite(UsosupdaterTest))
    test_suite.addTest(unittest.makeSuite(ApiCoursesGradesTest))
    test_suite.addTest(unittest.makeSuite(ApiUserTest))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
