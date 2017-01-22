# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiTTTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiTTTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user()

    # new TT endpoint test

    @gen_test(timeout=20)
    def testTTMonth(self):
        yield self.assertOK(self.get_url('/ttusers/2017-01-20'))

    @gen_test(timeout=20)
    def testTTFake(self):
        yield self.assertFail(self.get_url('/ttusers/Fake'))

    # lecturers

    @gen_test(timeout=20)
    def testTTLecturersFake(self):
        yield self.assertFail(self.get_url('/ttlecturers/Fake/Fake'))

    @gen_test(timeout=20)
    def testTTLecturers(self):
        yield self.assertOK(self.get_url('/ttlecturers/1/2017-01-20'))

