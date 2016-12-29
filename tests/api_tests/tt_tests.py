# coding=utf-8

from datetime import datetime

from tornado.testing import gen_test

from tests.api_tests.base import AbstractApplicationTestBase

USER_DOC = {"access_token_secret": "cjFPyKjDk5GNTcqpxeEsfWuhd9bLApbaw7ECfqHv",
            "access_token_key": "VkyGQdtREPCvULQnQ4uF",
            "usos_user_id": "1279833",
            "user_created": datetime.now(),
            "name": "dzizes dzizes",
            "created_time": datetime.now(),
            "update_time": datetime.now(),
            "email": "testowy@gmail.com",
            "usos_id": "DEMO",
            "usos_paired": True,
            "user_type": "google",
            "google": {
                "picture": "https://lh3.googleusercontent.com/-f7w-r4iF8DM/AAAAAAAAAAI/AAAAAAAALGo/GDUJeUaHtUo/photo.jpg",
                "email": "testowy@gmail.com",
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImI5Njk3MmI4NjUwZDFjOGNhMmM1NDA0MzhlNGQ5MzUxNzY5ODk0MzIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6Ik83MkVjcGVrSVVPT2xGMWlIVXAxQUEiLCJhdWQiOiI4OTY3NjU3Njg2MjgtYjF0dXQ1ZzZoamluN2lpbjZobjRxbzhsdDNiNmlobHQuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTI1MjEwOTU0NjU0NTA5OTg1MTciLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXpwIjoiODk2NzY1NzY4NjI4LWIxdHV0NWc2aGppbjdpaW42aG40cW84bHQzYjZpaGx0LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiZW1haWwiOiJkeml6ZXM0NTFAZ21haWwuY29tIiwiaWF0IjoxNDcxODY3ODg3LCJleHAiOjE0NzE4NzE0ODd9.PwLfed8_52aydutvkREXHsBcaYHsF2U4E1UQEo5PdaAOE6aJigWqeh4v8GRtYy3IxDzja9j75rkbFP0Hch0elyIDUxrWS2lnDile5TYqiyoXGEfEw6ADvZVq8dVklbGYqg_H5G32tuLUERyleYBWYrPrjJGIRNlEoD2w-Cou2YeHysQl9GNKZl7vmS62HPClPF0jXDQGag_ziHAKBRxl5d4JwC4h3Sg4XunUdUsoq1Ey5F_rAzo5cggCOsQCpXcuSGGWc7YDCDCGBW5JsJsPv6mAi1jgepP5OETMGHC_yrXmQcjUJyctooKVRLRmaLNujlTe95ne-4v8psKOXH_nZQ",
                "access_token": "ya29.CjBHA89EmKP6zkOMrW0K7a3INpF-oZjtyV02aAtwNhrNwqc0_hJM9XoQbuyTbOyCC3I",
                "token_type": "Bearer",
                "name": "testowy@gmail.com",
                "expires_in": datetime.now()},
            }

TOKEN_DOC = {"locale": "pl",
             "name": "imie nazwisko",
             "iat": "1471441024",
             "picture": "https://lh3.googleusercontent.com/-f7w-r4iF8DM/AAAAAAAAAAI/AAAAAAAALGo/GDUJeUaHtUo/photo.jpg",
             "email": "testowy@gmail.com",
             "sub": "101491399228182082844",
             "created_time": datetime.now(),
             "update_time": datetime.now(),
             "login_type": "GOOGLE",
             "alg": "RS256",
             "usos_id": "UWR",
             "given_name": "dzizes451@gmail.com",
             "iss": "https://accounts.google.com",
             "family_name": "dzizes451",
             "email_verified": "true",
             "kid": "a3c737a7b795026217d05be98f8736bd09a69d0d",
             "aud": "896765768628-4tb5sl5l115mcjbavsvgjiinovtifm6p.apps.googleusercontent.com",
             "exp": "1471444624",
             "azp": "896765768628-e6ja58ug43hacq7usqnmn5uakgvnorvd.apps.googleusercontent.com"}


class ApiTTTest(AbstractApplicationTestBase):
    def setUp(self):
        super(ApiTTTest, self).setUp()
        self.prepareDatabase(self.config)
        self.insert_user(config=self.config, user_doc=USER_DOC, token_doc=TOKEN_DOC)

    @gen_test(timeout=30)
    def testTT(self):
        yield self.fetch_assert(self.get_url('/tt/2015-05-05'))

    @gen_test(timeout=30)
    def testTTLecturersFalse(self):
        yield self.fetch_assert(self.get_url('/tt/2015-05-05?lecturers_info=False'))

    @gen_test(timeout=30)
    def testTTDays(self):
        yield self.fetch_assert(self.get_url('/tt/2015-05-05?days=1'))

    @gen_test(timeout=30)
    def testTTFake(self):
        yield self.fetch_assert(self.get_url('/tt/Fake'))
