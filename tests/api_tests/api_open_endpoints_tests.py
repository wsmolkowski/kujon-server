# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiRestTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiRestTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

    @gen_test(timeout=1)
    def testConfig(self):
        response = yield self.http_client.fetch(self.get_url('/config'))
        self.assert_api_response(response)

    @gen_test(timeout=1)
    def testUsoses(self):
        response = yield self.http_client.fetch(self.get_url('/usoses'))
        self.assert_api_response(response)

    @gen_test(timeout=3)
    def testUsosesAll(self):
        response = yield self.http_client.fetch(self.get_url('/usosesall'))
        self.assert_api_response(response)
