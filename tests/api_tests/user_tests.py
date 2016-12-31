# coding=utf-8
from tornado.testing import gen_test

from commons.constants import fields
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
        yield self.fetch_assert(self.get_url('/users/Fake'), assert_response=False)

    @gen_test(timeout=10)
    def testUsersInfoPhotosById(self):
        user_doc = yield self.fetch_assert(self.get_url('/users'))
        # get photo_id from PHOTO_URL field
        photo_id = user_doc['data'][fields.PHOTO_URL].split('/', 4)[4]
        yield self.fetch_assert(self.get_url('/users_info_photos/{0}'.format(photo_id)), contenttype='image/jpeg')

    @gen_test(timeout=10)
    def testUsersInfoAll(self):
        yield self.fetch_assert(self.get_url('/usersinfoall'))