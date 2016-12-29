# coding=utf-8

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase


class ApiCoursesTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiCoursesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config)

    @gen_test(timeout=10)
    def testCourseseditions(self):
        yield self.fetch_assert(self.get_url('/users'))

    @gen_test(timeout=10)
    def testCourseseditions(self):
        yield self.fetch_assert(self.get_url('/usersinfoall'))

    @gen_test(timeout=10)
    def testCourseseditions(self):
        yield self.fetch_assert(self.get_url('/courseseditions'))

    @gen_test(timeout=10)
    def testCourseseditionsbyterm(self):
        yield self.fetch_assert(self.get_url('/courseseditionsbyterm'))

    @gen_test(timeout=10)
    def testCourseseditionsCourseIdTermId(self):
        yield self.fetch_assert(self.get_url('/courseseditions/4018-WYK18E-OG/2014'))

    @gen_test(timeout=10)
    def testCourses(self):
        yield self.fetch_assert(self.get_url('/courses/123'))

    @gen_test(timeout=10)
    def testGrades(self):
        yield self.fetch_assert(self.get_url('/grades'))

    @gen_test(timeout=10)
    def testGradesByTerm(self):
        yield self.fetch_assert(self.get_url('/gradesbyterm'))

    @gen_test(timeout=10)
    def testTerms(self):
        yield self.fetch_assert(self.get_url('/terms'))

    @gen_test(timeout=10)
    def testTermsSingle(self):
        yield self.fetch_assert(self.get_url('/terms/123'))

    @gen_test(timeout=10)
    def testTermsLecturers(self):
        yield self.fetch_assert(self.get_url('/lecturers'))

    @gen_test(timeout=10)
    def testTermsLecturersSingle(self):
        yield self.fetch_assert(self.get_url('/lecturers/123'))

    @gen_test(timeout=10)
    def testTermsProgrammes(self):
        yield self.fetch_assert(self.get_url('/programmes'))

    @gen_test(timeout=10)
    def testTermsProgrammesSingle(self):
        yield self.fetch_assert(self.get_url('/programmes/123'))

    @gen_test(timeout=10)
    def testTermsFaculties(self):
        yield self.fetch_assert(self.get_url('/faculties'))

    @gen_test(timeout=10)
    def testTermsFacultiesSingle(self):
        yield self.fetch_assert(self.get_url('/faculties/123'))

    @gen_test(timeout=10)
    def testTermsTheses(self):
        yield self.fetch_assert(self.get_url('/theses'))

    @gen_test(timeout=10)
    def testTermsCrstests(self):
        yield self.fetch_assert(self.get_url('/crstests'))

    @gen_test(timeout=10)
    def testTermsCrstestsSingle(self):
        yield self.fetch_assert(self.get_url('/crstests/123'))

    @gen_test(timeout=10)
    def testTermsSubscriptions(self):
        yield self.fetch_assert(self.get_url('/subscriptions'))

    @gen_test(timeout=10)
    def testTermsMessages(self):
        yield self.fetch_assert(self.get_url('/messages'))
