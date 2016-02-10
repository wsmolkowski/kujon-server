from tornado.testing import AsyncTestCase, gen_test

from usosapi.usosutils import usosasync


class UsosAsyncTest(AsyncTestCase):
    def setUp(self):
        super(UsosAsyncTest, self).setUp()

    def tearDown(self):
        self.stop()

    @gen_test
    def testGetTermInfo(self):
        # assume
        term_id = "2004/TZ"
        base_url = "https://usosapps.uw.edu.pl/"

        # when
        result = yield usosasync.get_term_info(base_url, term_id)

        # then
        self.assertNotEqual(0, result)


    @gen_test
    def testGetUnitInfo(self):
        # assume
        unit_id = "15099"
        base_url = "https://usosapps.uw.edu.pl/"

        # when
        result = yield usosasync.get_courses_units(base_url, unit_id)

        # then
        self.assertNotEqual(0, result)


    @gen_test
    def testGetClassTypes(self):
        # assume
        base_url = "https://usosapps.uw.edu.pl/"

        # when
        result = yield usosasync.get_courses_classtypes(base_url)

        # then
        self.assertNotEqual(0, result)
