# coding=utf-8

from tornado.testing import gen_test

from tests.base import AbstractApplicationTestBase


class ApiUserTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiUserTest, self).setUp()
        self.prepareDatabase(self.config)
        self.inser_user(config=self.config)

    @gen_test(timeout=30)
    def testUsers(self):
        yield self.fetch_assert(self.get_url('/users'))

    @gen_test(timeout=30)
    def testUsers1(self):
        yield self.fetch_assert(self.get_url('/users/1'))

    @gen_test(timeout=30)
    def testUsersFake(self):
        yield self.fetch_assert(self.get_url('/users/Fake'))

    @gen_test(timeout=30)
    def testUsersInfoPhoto(self):
        yield self.fetch_assert(self.get_url('/users_info_photos/123'))
