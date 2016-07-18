# coding=utf-8
import datetime
import unittest

from bson.objectid import ObjectId

from commons import utils


class SerializationTest(unittest.TestCase):
    def testSerialization(self):
        # assume
        data = {u'_id': ObjectId("56c4b3dcc4f9d23ed8ef19d2"),
                u'picture': u'https://lh3.googleusercontent.com/-f7w-r4iF8DM/AAAAAAAAAAI/AAAAAAAALGo/GDUJeUaHtUo/photo.jpg',
                u'update_time': datetime.datetime(2016, 2, 17, 18, 55, 2, 192000), u'last_name': u'Smo\u0142kowski',
                u'student_status': 1, u'name': u'dzizes dzizes', u'locale': u'en', u'first_name': u'Wojciech',
                u'id': u'1613', u'user_created': datetime.datetime(2016, 2, 17, 18, 54, 36, 710000),
                u'given_name': u'dzizes', u'student_programmes': [{u'id': u'1264', u'programme': {
                u'description': {u'en': u'Vocational Studies in Computer Science',
                                 u'pl': u'Zawodowe Studia Informatyki, niestacjonarne (wieczorowe), pierwszego stopnia'},
                u'id': u'WZ-ZSI'}}, {u'id': u'50932', u'programme': {
                u'description': {u'en': u'Computer Science, part-time evening studies, second cycle programme',
                                 u'pl': u'Magisterskie Studia Uzupe\u0142niaj\u0105ce z Informatyki, niestacjonarne (wieczorowe), drugiego stopnia'},
                u'id': u'WU-MSUI'}}], u'has_photo': False, u'student_number': u'2085', u'email': u'dzizes451@gmail.com',
                'user_email': u'ws2085@students.mimuw.edu.pl'}

        # when
        result = utils.serialize_dictionary(data)

        # then
        expected = {
            u'picture': u'https://lh3.googleusercontent.com/-f7w-r4iF8DM/AAAAAAAAAAI/AAAAAAAALGo/GDUJeUaHtUo/photo.jpg',
            u'update_time': '2016-02-17 18:55:02', u'last_name': u'Smo\u0142kowski', u'student_status': 1,
            u'name': u'dzizes dzizes', u'locale': u'en', u'first_name': u'Wojciech', u'email': u'dzizes451@gmail.com',
            u'user_created': '2016-02-17 18:54:36', u'given_name': u'dzizes', u'student_programmes': [{u'id': u'1264',
                                                                                                        u'programme': {
                                                                                                            u'description': {
                                                                                                                u'en': u'Vocational Studies in Computer Science',
                                                                                                                u'pl': u'Zawodowe Studia Informatyki, niestacjonarne (wieczorowe), pierwszego stopnia'},
                                                                                                            u'id': u'WZ-ZSI'}},
                                                                                                       {u'id': u'50932',
                                                                                                        u'programme': {
                                                                                                            u'description': {
                                                                                                                u'en': u'Computer Science, part-time evening studies, second cycle programme',
                                                                                                                u'pl': u'Magisterskie Studia Uzupe\u0142niaj\u0105ce z Informatyki, niestacjonarne (wieczorowe), drugiego stopnia'},
                                                                                                            u'id': u'WU-MSUI'}}],
            u'has_photo': False, u'student_number': u'2085', u'id': u'1613',
            'user_email': u'ws2085@students.mimuw.edu.pl'}

        self.assertEquals(expected, result)
