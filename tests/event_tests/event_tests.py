# coding=utf-8

from datetime import datetime

import motor.motor_tornado

from commons.AESCipher import AESCipher
from commons.constants import fields
from event.server import get_application
from tests.base import BaseTestClass

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


class EventTest(BaseTestClass):
    def get_app(self):
        application = get_application(self.config)
        db = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]
        application.settings[fields.APPLICATION_DB] = db
        application.settings[fields.APPLICATION_CONFIG] = self.config
        application.settings[fields.APPLICATION_AES] = AESCipher(self.config.AES_SECRET)

        return application

    # @gen_test(timeout=50)
    def testEvent(self):
        # assume
        challange = 'BKHeL7VXuPDttqDVzWne'
        self.prepareDatabase(self.config)

        result = self.inser_user(config=self.config, user_doc=USER_DOC)
        user_id = str(result[0])

        aes = AESCipher(self.config.AES_SECRET)
        verify_token = aes.encrypt(user_id).decode()

        url = '/{0}?hub.mode=subscribe&hub.challenge={1}&hub.verify_token={2}'.format(
            USER_DOC[fields.USOS_ID], challange, verify_token)

        # when
        # result = yield self.client.fetch(self.get_url(url))
        result = self.fetch(url, method='GET', headers={
            fields.MOBILE_X_HEADER_EMAIL: USER_DOC['email'],
            fields.MOBILE_X_HEADER_TOKEN: USER_DOC['google']['access_token'],
            fields.MOBILE_X_HEADER_REFRESH: 'True',
        })

        # then
        self.assertEquals(challange, result.body)
