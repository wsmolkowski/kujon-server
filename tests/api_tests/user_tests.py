# coding=utf-8

from tornado.testing import gen_test

from tests.base import AbstractApplicationTestBase


class ApiUserTest(AbstractApplicationTestBase):
    @gen_test(timeout=30)
    def testUsers(self):
        self.fetch_assert(self.get_url('/users'))

    @gen_test(timeout=30)
    def testUsers1(self):
        self.fetch_assert(self.get_url('/users/1'))

    @gen_test(timeout=30)
    def testUsersFake(self):
        self.fetch_assert(self.get_url('/users/Fake'))

    @gen_test(timeout=30)
    def testUsersInfoPhoto(self):
        self.fetch_assert(self.get_url('/users_info_photos/123'))
