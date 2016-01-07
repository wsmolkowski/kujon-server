import unittest

from usos import USOSUpdater


class UsosupdaterTest(unittest.TestCase):


    def testShouldGetGradesWoj(self):
        consumer_key = 'KBt6uWPWUekUzFtNTyY9'
        consumer_secret = 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG'
        usosapi_base_url = 'https://usosapps.uw.edu.pl/'

        # You may want to hardcode these values, so you won't need to reauthorize ***
        access_token_key = '3ShYQv8LyvgeXthKJzmJ'
        access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'

        updater = USOSUpdater(3, usosapi_base_url, consumer_key, consumer_secret, access_token_key, access_token_secret)

        url = "services/grades/course_edition?course_id=E-2IZ2-1004-s3&term_id=2014/15-1"
        data = updater.request(url)

        self.assertIsNotNone(data)

    def testShouldGetGrades(self):
        consumer_key = 'equujDB5ZLzTmPfcy2c2'
        consumer_secret = 'PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA'
        usosapi_base_url = 'https://api.usos.tu.kielce.pl/'

        access_token_key = 'uXLyCGpp5zfHPH4z4brg'
        access_token_secret = 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'

        updater = USOSUpdater(3, usosapi_base_url, consumer_key, consumer_secret, access_token_key, access_token_secret)

        url = "services/grades/course_edition?course_id=E-2IZ2-1004-s3&term_id=2014/15-1"
        data = updater.request(url)

        print data
        self.assertIsNotNone(data)


    def testShouldGetGradesLuk(self):
        consumer_key = 'equujDB5ZLzTmPfcy2c2'
        consumer_secret = 'PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA'
        usosapi_base_url = 'https://api.usos.tu.kielce.pl/'

        # You may want to hardcode these values, so you won't need to reauthorize ***
        access_token_key = 'uXLyCGpp5zfHPH4z4brg'
        access_token_secret = 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'

        updater = USOSUpdater(3, usosapi_base_url, consumer_key, consumer_secret, access_token_key, access_token_secret)

        url = "services/grades/course_edition?course_id=E-2IZ2-1004-s3&term_id=2014/15-1"
        data = updater.request(url)

        self.assertIsNotNone(data)