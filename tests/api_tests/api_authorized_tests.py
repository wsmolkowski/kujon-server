# coding=utf-8

from random import randint

from tornado.testing import gen_test

from commons.constants import fields
from tests.api_tests.base import AbstractApplicationTestBase


class ApiCoursesTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiCoursesTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user()
        self.random = randint(0, 9999)

    @gen_test(timeout=30)
    def testUsers(self):
        yield self.assertOK(self.get_url('/users'))

    @gen_test(timeout=30)
    def testCourseseditions(self):
        yield self.assertOK(self.get_url('/usersinfoall'))

    @gen_test(timeout=30)
    def testCourseseditions(self):
        yield self.assertOK(self.get_url('/courseseditions'))

    @gen_test(timeout=30)
    def testCourseseditionsbyterm(self):
        yield self.assertOK(self.get_url('/courseseditionsbyterm'))

    @gen_test(timeout=30)
    def testCourseseditionsCourseIdTermId(self):
        yield self.assertFail(self.get_url('/courseseditions/X/y'))

    @gen_test(timeout=30)
    def testCourses(self):
        result = yield self.assertOK(self.get_url('/courseseditions'))
        course_id = result['data'][0][fields.COURSE_ID]
        yield self.assertFail(self.get_url('/courses/{0}'.format(course_id)))

    @gen_test(timeout=30)
    def testGrades(self):
        yield self.assertOK(self.get_url('/grades'))

    @gen_test(timeout=30)
    def testGradesByTerm(self):
        yield self.assertOK(self.get_url('/gradesbyterm'))

    @gen_test(timeout=30)
    def testTerms(self):
        yield self.assertOK(self.get_url('/terms'))

    @gen_test(timeout=30)
    def testTermsSingle(self):
        result = yield self.assertOK(self.get_url('/terms'))
        term_id = result['data'][0][fields.TERM_ID]
        yield self.assertOK(self.get_url('/terms/{0}'.format(term_id)))

    @gen_test(timeout=30)
    def testTermsLecturers(self):
        yield self.assertOK(self.get_url('/lecturers'))

    @gen_test(timeout=30)
    def testTermsLecturersSingle(self):
        yield self.assertOK(self.get_url('/lecturers/1480001'.format(self.random)))

    @gen_test(timeout=30)
    def testTermsProgrammes(self):
        yield self.assertOK(self.get_url('/programmes'))

    @gen_test(timeout=30)
    def testTermsProgrammesSingle(self):
        yield self.assertFail(self.get_url('/programmes/{0}'.format(self.random)))

    @gen_test(timeout=30)
    def testTermsFaculties(self):
        yield self.assertOK(self.get_url('/faculties'))

    @gen_test(timeout=30)
    def testTermsFacultiesSingle(self):
        yield self.assertFail(self.get_url('/faculties/{0}'.format(self.random)))

    @gen_test(timeout=30)
    def testTermsTheses(self):
        yield self.assertOK(self.get_url('/theses'))

    @gen_test(timeout=30)
    def testTermsCrstests(self):
        yield self.assertOK(self.get_url('/crstests'))

    @gen_test(timeout=30)
    def testTermsCrstestsSingle(self):
        result = yield self.assertOK(self.get_url('/crstests'))
        if len(result['data']['tests']) > 0:
            id = result['data']['tests'][0]
            yield self.assertOK(self.get_url('/crstests/{0}'.format(id)))
        else:
            yield self.assertFail(self.get_url('/crstests/{0}'.format(self.random)))

    @gen_test(timeout=30)
    def testTermsSubscriptions(self):
        yield self.assertOK(self.get_url('/subscriptions'))

    @gen_test(timeout=30)
    def testTermsMessages(self):
        yield self.assertOK(self.get_url('/messages'))
