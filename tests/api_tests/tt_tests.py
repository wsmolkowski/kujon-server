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
        yield self.assertOK(self.get_url('/tt/2015-05-05'))

    @gen_test(timeout=10)
    def testTTLecturersFalse(self):
        yield self.assertOK(self.get_url('/tt/2015-05-05?lecturers_info=False'))

    @gen_test(timeout=10)
    def testTTDays(self):
        yield self.assertOK(self.get_url('/tt/2015-05-05?days=1'))

    @gen_test(timeout=10)
    def testTTFake(self):
        yield self.assertOK(self.get_url('/tt/Fake'))
