# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiSearchTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiSearchTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

    @gen_test(timeout=10)
    def testSearchUsers(self):
        yield self.fetch_assert(self.get_url('/search/users/adam'))

    @gen_test(timeout=10)
    def testSearchCourses(self):
        yield self.fetch_assert(self.get_url('/search/courses/mate'))

    @gen_test(timeout=10)
    def testSearchFaculties(self):
        yield self.fetch_assert(self.get_url('/search/faculties/Wydz'))

    @gen_test(timeout=5)
    def testSearchProgrammes(self):
        yield self.fetch_assert(self.get_url('/search/programmes/geograf'))

    @gen_test(timeout=10)
    def testSearchTheses(self):
        yield self.fetch_assert(self.get_url('/search/theses/geograf'))
