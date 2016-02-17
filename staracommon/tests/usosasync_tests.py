from tornado.testing import AsyncTestCase, gen_test

from staracommon.usosutils.usosasync import UsosAsync


class UsosAsyncTest(AsyncTestCase):
    def setUp(self):
        self.usosAsync = UsosAsync()
        super(UsosAsyncTest, self).setUp()

    def tearDown(self):
        self.stop()

    @gen_test(timeout=100)
    def testGetTermInfo(self):
        # assume
        term_id = "2004/TZ"
        base_url = "https://usosapps.uw.edu.pl/"

        # when
        result = yield self.usosAsync.get_term_info(base_url, term_id)

        # then
        self.assertNotEqual(0, result)


    @gen_test(timeout=100)
    def testGetUnitInfo(self):
        # assume
        unit_id = "15099"
        base_url = "https://usosapps.uw.edu.pl/"

        # when
        result = yield self.usosAsync.get_courses_units(base_url, unit_id)

        # then
        self.assertNotEqual(0, result)


    @gen_test(timeout=100)
    def testGetClassTypes(self):
        # assume
        base_url = "https://usosapps.uw.edu.pl/"

        # when
        result = yield self.usosAsync.get_courses_classtypes(base_url)

        # then
        self.assertNotEqual(0, result)
