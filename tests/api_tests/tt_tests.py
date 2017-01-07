# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiTTTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiTTTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

    @gen_test(timeout=10)
    def testTT(self):
        yield self.assertOK(self.get_url('/tt/2016-01-20'))

    @gen_test(timeout=10)
    def testTTLecturersFalse(self):
        yield self.assertOK(self.get_url('/tt/2016-01-20?lecturers_info=False'))

    @gen_test(timeout=10)
    def testTTDays(self):
        yield self.assertOK(self.get_url('/tt/2016-01-20?days=1'))

    @gen_test(timeout=10)
    def testTTFake(self):
        yield self.assertOK(self.get_url('/tt/Fake'))

    # lecutrers

    @gen_test(timeout=10)
    def testTTLecturersFake(self):
        yield self.assertFail(self.get_url('/ttlecturers/Fake/Fake'))

    @gen_test(timeout=10)
    def testTTLecturers(self):
        yield self.assertOK(self.get_url('/ttlecturers/1/2016-01-20'))

