import unittest
from datetime import datetime

import constants
from mongo_utils import Dao
from usosupdater import USOSUpdater

USOSTESTUSERS = {
    '1264': {
        constants.USOS_ID: 'UW',
        constants.ACCESS_TOKEN_KEY: '3ShYQv8LyvgeXthKJzmJ',
        constants.ACCESS_TOKEN_SECRET: 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'
    },
    '15822': {
        constants.USOS_ID: 'PS',
        constants.ACCESS_TOKEN_KEY: 'uXLyCGpp5zfHPH4z4brg',
        constants.ACCESS_TOKEN_SECRET: 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'
    }
}

class UsosupdaterTest(unittest.TestCase):

    def setUp(self):
        self.dao = Dao()

    def testShouldGetUserInformation(self):
        # assume
        usos = self.dao.get_usos('UW')

        # when
        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
            '3ShYQv8LyvgeXthKJzmJ', 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        result = updater.request_user_info()
        expected = [u'first_name', u'last_name', u'student_status', u'sex', u'titles', u'has_email', u'student_programmes', u'id', u'student_number', u'email']

        # then
        self.assertListEqual(expected, result.keys())


    def testShouldGetCourseEditions(self):
        # assume
        usos = self.dao.get_usos('UW')

        # when
        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                              '3ShYQv8LyvgeXthKJzmJ', 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        # TODO: sprawdzic co zawraca
        result = updater.request_curse_info()

        # then
        self.assertListEqual([u'course_editions'], result.keys())


    def testShouldGetPlan(self):
        # assume
        usos = self.dao.get_usos('UW')

        # when
        updater = USOSUpdater(usos[constants.URL], usos[constants.CONSUMER_KEY], usos[constants.CONSUMER_SECRET],
                              '3ShYQv8LyvgeXthKJzmJ', 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y')
        url = 'services/tt/student?start=' + str(datetime.now().date()) + '&days=1'
        result = updater.request(url)

        # then
        self.assertIsNotNone(result)
        #self.assertListEqual([123444, ], result)