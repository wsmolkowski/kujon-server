# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiUserTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiUserTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

    @gen_test(timeout=1)
    def test_users(self):
        yield self.fetch_assert(self.get_url('/users'))

    @gen_test(timeout=1)
    def test_users_by_id(self):
        yield self.fetch_assert(self.get_url('/users/1'))

    @gen_test(timeout=1)
    def test_users_with_fake_id(self):
        yield self.fetch_assert(self.get_url('/users/Fake'))

    @gen_test(timeout=1)
    def test_users_info_photos_by_id(self):
        yield self.fetch_assert(self.get_url('/users_info_photos/123'))
