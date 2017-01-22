# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiSearchTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiSearchTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user()

    @gen_test(timeout=20)
    def testSearchUsers(self):
        yield self.assertOK(self.get_url('/search/users/adam'))

    @gen_test(timeout=20)
    def testSearchCourses(self):
        yield self.assertOK(self.get_url('/search/courses/mate'))

    @gen_test(timeout=20)
    def testSearchFaculties(self):
        yield self.assertOK(self.get_url('/search/faculties/Wydz'))

    @gen_test(timeout=20)
    def testSearchProgrammes(self):
        yield self.assertOK(self.get_url('/search/programmes/geograf'))

    @gen_test(timeout=20)
    def testSearchTheses(self):
        yield self.assertOK(self.get_url('/search/theses/geograf'))
