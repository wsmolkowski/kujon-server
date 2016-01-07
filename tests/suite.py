import unittest




def build_suite():

    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(BaseTests))

    return test_suite


if __name__ == '__main__':
    suite = build_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)