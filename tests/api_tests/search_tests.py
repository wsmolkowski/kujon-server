# coding=utf-8

from tornado.testing import gen_test

from tests.base import AbstractApplicationTestBase


class ApiSearchTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiSearchTest, self).setUp()
        self.prepareDatabase(self.config)
        self.inser_user(config=self.config)

    @gen_test(timeout=30)
    def termsSearchUsers(self):
        yield self.fetch_assert(self.get_url('/search/users/adam'))

    @gen_test(timeout=30)
    def termsSearchCourses(self):
        yield self.fetch_assert(self.get_url('/search/courses/geograf'))

    @gen_test(timeout=30)
    def termsSearchFaculties(self):
        yield self.fetch_assert(self.get_url('/search/faculties/adamini'))

    @gen_test(timeout=30)
    def termsSearchProgrammes(self):
        yield self.fetch_assert(self.get_url('/search/programmes/geograf'))

    @gen_test(timeout=30)
    def termsSearchTheses(self):
        yield self.fetch_assert(self.get_url('/search/theses/geograf'))
