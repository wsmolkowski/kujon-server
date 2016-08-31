# coding=utf-8

from tornado.testing import gen_test

from tests.base import AbstractApplicationTestBase


class ApiRestTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiRestTest, self).setUp()
        self.prepareDatabase(self.config)
        self.inser_user(config=self.config)

    @gen_test(timeout=30)
    def testConfig(self):
        response = yield self.http_client.fetch(self.get_url('/config'))
        self.assertApiResponse(response)

    @gen_test(timeout=30)
    def testUsoses(self):
        response = yield self.http_client.fetch(self.get_url('/usoses'))
        self.assertApiResponse(response)

    @gen_test(timeout=30)
    def testUsosesFail(self):
        response = yield self.http_client.fetch(self.get_url('/users'))
        self.assertApiResponseFail(response)

    @gen_test(timeout=30)
    def termsTheses(self):
        yield self.fetch_assert(self.get_url('/theses'))

    @gen_test(timeout=30)
    def termsCrstests(self):
        yield self.fetch_assert(self.get_url('/crstests'))

    @gen_test(timeout=30)
    def termsCrstestsSingle(self):
        yield self.fetch_assert(self.get_url('/crstests/123'))

    @gen_test(timeout=30)
    def termsSubscriptions(self):
        yield self.fetch_assert(self.get_url('/subscriptions'))

    @gen_test(timeout=30)
    def termsMessages(self):
        yield self.fetch_assert(self.get_url('/messages'))
