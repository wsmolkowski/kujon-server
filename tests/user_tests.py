from tornado.testing import AsyncHTTPTestCase
import server
import settings
TEST_PORT = 9999


class TestUser(AsyncHTTPTestCase):
    def get_app(self):
        app = server.Application()
        app.listen(TEST_PORT)
        return app


    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Hello, world from database usos-test2')


    def testShouldGetUser(self):

        # check call without arguments
        response = self.fetch('/api/user')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'arguments not supported')

        # check for good support of passed 4 usuported args
        response = self.fetch('/api/user?a=1&b=1&b=3&d=4')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'arguments not supported')

        #TODO: change this test to remove user, create user, check for user, and remove user
        # get data for existing user
        response = self.fetch('/api/user?user_id=2&usos_id=UW&access_token_key=3ShYQv8LyvgeXthKJzmJ&access_token_secret=JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '{"usos_data": {"first_name": "Wojciech", "last_name": "Smo\u0142kowski", "student_status": 1, "sex": "M", "email": "ws2085@students.mimuw.edu.pl", "titles": {"after": null, "before": null}, "has_email": true, "student_programmes": [{"id": "1264", "programme": {"description": {"en": "Vocational Studies in Computer Science", "pl": "Zawodowe Studia Informatyki, niestacjonarne (wieczorowe), pierwszego stopnia"}, "id": "WZ-ZSI"}}, {"id": "50932", "programme": {"description": {"en": "Computer Science, part-time evening studies, second cycle programme", "pl": "Magisterskie Studia Uzupe\u0142niaj\u0105ce z Informatyki, niestacjonarne (wieczorowe), drugiego stopnia"}, "id": "WU-MSUI"}}], "student_number": "2085", "id": "1613"}, "_id": {"$oid": "5690df3ec4f9d22fa83ddc04"}, "user_id": "2"}')
