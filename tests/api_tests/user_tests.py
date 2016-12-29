# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiUserTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiUserTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

    @gen_test(timeout=10)
    def testUsers(self):
        yield self.fetch_assert(self.get_url('/users'))

    @gen_test(timeout=10)
    def testUsersById(self):
        yield self.fetch_assert(self.get_url('/users/1'))

    @gen_test(timeout=10)
    def testUsersWithFakeId(self):
        yield self.fetch_assert(self.get_url('/users/Fake'))

    @gen_test(timeout=10)
    def testUsersInfoPhotosById(self):
        yield self.fetch_assert(self.get_url('/users_info_photos/123'))
