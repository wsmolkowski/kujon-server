# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiRestTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiRestTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user()

    @gen_test(timeout=5)
    def testConfig(self):
        yield self.assertOK(self.get_url('/config'))


    @gen_test(timeout=5)
    def testUsoses(self):
        yield self.assertOK(self.get_url('/usoses'))

    @gen_test(timeout=5)
    def testUsosesAll(self):
        yield self.assertOK(self.get_url('/usosesall'))
