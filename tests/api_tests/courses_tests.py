# coding=utf-8

from tornado.testing import gen_test

from tests.base import AbstractApplicationTestBase


class ApiCoursesTest(AbstractApplicationTestBase):
    @gen_test(timeout=30)
    def testCourseseditions(self):
        self.fetch_assert(self.get_url('/courseseditions'))

    @gen_test(timeout=30)
    def testCourseseditionsbyterm(self):
        self.fetch_assert(self.get_url('/courseseditionsbyterm'))

    @gen_test(timeout=30)
    def testCourseseditions(self):
        self.fetch_assert(self.get_url('/courseseditions/123/456'))

    @gen_test(timeout=30)
    def testCourses(self):
        self.fetch_assert(self.get_url('/courses/123'))

    @gen_test(timeout=30)
    def testGrades(self):
        self.fetch_assert(self.get_url('/grades'))

    @gen_test(timeout=30)
    def testGradesByTerm(self):
        self.fetch_assert(self.get_url('/gradesbyterm'))

    @gen_test(timeout=30)
    def terms(self):
        self.fetch_assert(self.get_url('/terms'))

    @gen_test(timeout=30)
    def termsSingle(self):
        self.fetch_assert(self.get_url('/terms/123'))

    @gen_test(timeout=30)
    def termsLecturers(self):
        self.fetch_assert(self.get_url('/lecturers'))

    @gen_test(timeout=30)
    def termsLecturersSingle(self):
        self.fetch_assert(self.get_url('/lecturers/123'))

    @gen_test(timeout=30)
    def termsTT(self):
        self.fetch_assert(self.get_url('/tt/2016-07-15'))

    @gen_test(timeout=30)
    def termsTTFake(self):
        self.fetch_assert(self.get_url('/tt/Fake'))

    @gen_test(timeout=30)
    def termsProgrammes(self):
        self.fetch_assert(self.get_url('/programmes'))

    @gen_test(timeout=30)
    def termsProgrammesSingle(self):
        self.fetch_assert(self.get_url('/programmes/123'))

    @gen_test(timeout=30)
    def termsFaculties(self):
        self.fetch_assert(self.get_url('/faculties'))

    @gen_test(timeout=30)
    def termsFacultiesSingle(self):
        self.fetch_assert(self.get_url('/faculties/123'))

    @gen_test(timeout=30)
    def termsTheses(self):
        self.fetch_assert(self.get_url('/theses'))

    @gen_test(timeout=30)
    def termsCrstests(self):
        self.fetch_assert(self.get_url('/crstests'))

    @gen_test(timeout=30)
    def termsCrstestsSingle(self):
        self.fetch_assert(self.get_url('/crstests/123'))

    @gen_test(timeout=30)
    def termsSubscriptions(self):
        self.fetch_assert(self.get_url('/subscriptions'))

    @gen_test(timeout=30)
    def termsMessages(self):
        self.fetch_assert(self.get_url('/messages'))
