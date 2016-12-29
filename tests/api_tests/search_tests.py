# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiSearchTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiSearchTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

    @gen_test(timeout=5)
    def testtermsSearchUsers(self):
        yield self.fetch_assert(self.get_url('/search/users/adam'))

    @gen_test(timeout=5)
    def testtermsSearchCourses(self):
        yield self.fetch_assert(self.get_url('/search/courses/geograf'))

    @gen_test(timeout=5)
    def testtermsSearchFaculties(self):
        yield self.fetch_assert(self.get_url('/search/faculties/adamini'))

    @gen_test(timeout=5)
    def testtermsSearchProgrammes(self):
        yield self.fetch_assert(self.get_url('/search/programmes/geograf'))

    @gen_test(timeout=5)
    def testtermsSearchTheses(self):
        yield self.fetch_assert(self.get_url('/search/theses/geograf'))
