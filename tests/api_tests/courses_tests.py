# coding=utf-8

from tornado.testing import gen_test

from tests.base import AbstractApplicationTestBase


class ApiCoursesTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiCoursesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.inser_user(config=self.config)

    @gen_test(timeout=30)
    def testCourseseditions(self):
        yield self.fetch_assert(self.get_url('/courseseditions'))

    @gen_test(timeout=30)
    def testCourseseditionsbyterm(self):
        yield self.fetch_assert(self.get_url('/courseseditionsbyterm'))

    @gen_test(timeout=30)
    def testCourseseditions(self):
        yield self.fetch_assert(self.get_url('/courseseditions/123/456'))

    @gen_test(timeout=30)
    def testCourses(self):
        yield self.fetch_assert(self.get_url('/courses/123'))

    @gen_test(timeout=30)
    def testGrades(self):
        yield self.fetch_assert(self.get_url('/grades'))

    @gen_test(timeout=30)
    def testGradesByTerm(self):
        yield self.fetch_assert(self.get_url('/gradesbyterm'))

    @gen_test(timeout=30)
    def testTerms(self):
        yield self.fetch_assert(self.get_url('/terms'))

    @gen_test(timeout=30)
    def testTermsSingle(self):
        yield self.fetch_assert(self.get_url('/terms/123'))

    @gen_test(timeout=30)
    def testTermsLecturers(self):
        yield self.fetch_assert(self.get_url('/lecturers'))

    @gen_test(timeout=30)
    def testTermsLecturersSingle(self):
        yield self.fetch_assert(self.get_url('/lecturers/123'))

    @gen_test(timeout=30)
    def testTermsProgrammes(self):
        yield self.fetch_assert(self.get_url('/programmes'))

    @gen_test(timeout=30)
    def testTermsProgrammesSingle(self):
        yield self.fetch_assert(self.get_url('/programmes/123'))

    @gen_test(timeout=30)
    def testTermsFaculties(self):
        yield self.fetch_assert(self.get_url('/faculties'))

    @gen_test(timeout=30)
    def testTermsFacultiesSingle(self):
        yield self.fetch_assert(self.get_url('/faculties/123'))

    @gen_test(timeout=30)
    def testTermsTheses(self):
        yield self.fetch_assert(self.get_url('/theses'))

    @gen_test(timeout=30)
    def testTermsCrstests(self):
        yield self.fetch_assert(self.get_url('/crstests'))

    @gen_test(timeout=30)
    def testTermsCrstestsSingle(self):
        yield self.fetch_assert(self.get_url('/crstests/123'))

    @gen_test(timeout=30)
    def testTermsSubscriptions(self):
        yield self.fetch_assert(self.get_url('/subscriptions'))

    @gen_test(timeout=30)
    def testTermsMessages(self):
        yield self.fetch_assert(self.get_url('/messages'))
