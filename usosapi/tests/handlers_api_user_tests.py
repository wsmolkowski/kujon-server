from tests_base import TestBaseClassApp

class ApiUserTest(TestBaseClassApp):

    def testEmptyUserShouldReturn404(self):
        response = self.fetch('/api/user')
        self.assertEqual(response.code, 400)

    def testShouldNotGetUser(self):
        response = self.fetch('/api/user?a=1&b=1&c=3&d=4')
        self.assertEqual(response.code, 400)

    def testShouldFailForFakeUser(self):
        response = self.fetch('/api/user?mobile_id=FAKE&b=1&c=3&d=4')
        self.assertEqual(response.code, 400)

    def testShouldGetUser(self):
        response = self.fetch("/api/user?{0}".format(self.auth_uri))
        self.assertEqual(response.code, 200)
        self.assertTrue('"mobile_id": "{0}"'.format(self.mobile_id) in response.body)
        self.assertTrue('"usos_id": "1613"' in response.body)



