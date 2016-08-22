# coding=utf-8

from tornado.testing import gen_test

from commons.tests.tests_base import TestBaseClassApp


class ApiTest(TestBaseClassApp):
    @gen_test(timeout=1000)
    def testConfig(self):
        response = yield self.http_client.fetch(self.get_url('/config'))
        self.assertApiResponse(response)

    @gen_test(timeout=1000)
    def testUsoses(self):
        response = yield self.http_client.fetch(self.get_url('/usoses'))
        self.assertApiResponse(response)

    @gen_test(timeout=1000)
    def testUsosesFail(self):
        response = yield self.http_client.fetch(self.get_url('/users'))
        self.assertApiResponseFail(response)

    @gen_test(timeout=1000)
    def testUsers(self):
        self.fetch_assert(self.get_url('/users'))

    @gen_test(timeout=1000)
    def testUsers1(self):
        self.fetch_assert(self.get_url('/users/1'))

    @gen_test(timeout=1000)
    def testUsersFake(self):
        self.fetch_assert(self.get_url('/users/Fake'))

    @gen_test(timeout=1000)
    def testUsersInfoPhoto(self):
        self.fetch_assert(self.get_url('/users_info_photos/123'))

    @gen_test(timeout=1000)
    def testCourseseditions(self):
        self.fetch_assert(self.get_url('/courseseditions'))

    @gen_test(timeout=1000)
    def testCourseseditionsbyterm(self):
        self.fetch_assert(self.get_url('/courseseditionsbyterm'))

    @gen_test(timeout=1000)
    def testCourseseditions(self):
        self.fetch_assert(self.get_url('/courseseditions/123/456'))

    @gen_test(timeout=1000)
    def testCourses(self):
        self.fetch_assert(self.get_url('/courses/123'))

    @gen_test(timeout=1000)
    def testGrades(self):
        self.fetch_assert(self.get_url('/grades'))

    @gen_test(timeout=1000)
    def testGradesByTerm(self):
        self.fetch_assert(self.get_url('/gradesbyterm'))

    @gen_test(timeout=1000)
    def terms(self):
        self.fetch_assert(self.get_url('/terms'))

    @gen_test(timeout=1000)
    def termsSingle(self):
        self.fetch_assert(self.get_url('/terms/123'))

    @gen_test(timeout=1000)
    def termsLecturers(self):
        self.fetch_assert(self.get_url('/lecturers'))

    @gen_test(timeout=1000)
    def termsLecturersSingle(self):
        self.fetch_assert(self.get_url('/lecturers/123'))

    @gen_test(timeout=1000)
    def termsTT(self):
        self.fetch_assert(self.get_url('/tt/2016-07-15'))

    @gen_test(timeout=1000)
    def termsTTFake(self):
        self.fetch_assert(self.get_url('/tt/Fake'))

    @gen_test(timeout=1000)
    def termsProgrammes(self):
        self.fetch_assert(self.get_url('/programmes'))

    @gen_test(timeout=1000)
    def termsProgrammesSingle(self):
        self.fetch_assert(self.get_url('/programmes/123'))

    @gen_test(timeout=1000)
    def termsFaculties(self):
        self.fetch_assert(self.get_url('/faculties'))

    @gen_test(timeout=1000)
    def termsFacultiesSingle(self):
        self.fetch_assert(self.get_url('/faculties/123'))

    @gen_test(timeout=1000)
    def termsSearchUsers(self):
        self.fetch_assert(self.get_url('/search/users/adam'))

    @gen_test(timeout=1000)
    def termsSearchCourses(self):
        self.fetch_assert(self.get_url('/search/courses/geograf'))

    @gen_test(timeout=1000)
    def termsSearchFaculties(self):
        self.fetch_assert(self.get_url('/search/faculties/adamini'))

    @gen_test(timeout=1000)
    def termsSearchProgrammes(self):
        self.fetch_assert(self.get_url('/search/programmes/geograf'))

    @gen_test(timeout=1000)
    def termsSearchTheses(self):
        self.fetch_assert(self.get_url('/search/theses/geograf'))

    @gen_test(timeout=1000)
    def termsTheses(self):
        self.fetch_assert(self.get_url('/theses'))

    @gen_test(timeout=1000)
    def termsCrstests(self):
        self.fetch_assert(self.get_url('/crstests'))

    @gen_test(timeout=1000)
    def termsCrstestsSingle(self):
        self.fetch_assert(self.get_url('/crstests/123'))

    @gen_test(timeout=1000)
    def termsSubscriptions(self):
        self.fetch_assert(self.get_url('/subscriptions'))

    @gen_test(timeout=1000)
    def termsMessages(self):
        self.fetch_assert(self.get_url('/messages'))
