# coding=utf-8

from commons.tests.tests_base import TestBaseClassApp


class ApiTermsTest(TestBaseClassApp):
    def testEmptyUserShouldReturn404(self):
        response = self.fetch('/api/terms/')
        self.assertEqual(response.code, 404)

    def testShouldReturnGivenTerm(self):
        response = self.fetch("/api/terms/2004?{0}".format(self.auth_uri))
        self.assertTrue('Rok akademicki 2004/05' in response.body)
        self.assertEqual(response.code, 200)
        response = self.fetch("/api/terms/2003%2FTJ?{0}".format(self.auth_uri))
        self.assertTrue('Trymestr jesienny 2003/04' in response.body)
        self.assertEqual(response.code, 200)

    def testShouldNotGetTermForFakeParams(self):
        response = self.fetch('/api/terms/FAKE?user_id=FAKE&a=1&b=1&c=3&d=4')
        self.assertEqual(response.code, 400)
        response = self.fetch('/api/terms/FAKE?mobile_id=FAKE&user_id=FAKE&b=1&c=3&d=4')
        self.assertEqual(response.code, 400)
        response = self.fetch("/api/terms/FAKE?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 400)
