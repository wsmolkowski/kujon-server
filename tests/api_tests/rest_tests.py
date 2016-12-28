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
    def testUsosesFail(self):
        response = yield self.http_client.fetch(self.get_url('/users'))
        self.assert_api_response_fail(response)

    @gen_test(timeout=3)
    def termsTheses(self):
        yield self.fetch_assert(self.get_url('/theses'))

    @gen_test(timeout=3)
    def termsCrstests(self):
        yield self.fetch_assert(self.get_url('/crstests'))

    @gen_test(timeout=3)
    def termsCrstestsSingle(self):
        yield self.fetch_assert(self.get_url('/crstests/123'))

    @gen_test(timeout=3)
    def termsSubscriptions(self):
        yield self.fetch_assert(self.get_url('/subscriptions'))

    @gen_test(timeout=3)
    def termsMessages(self):
        yield self.fetch_assert(self.get_url('/messages'))
