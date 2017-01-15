# coding=utf-8

import unittest

from event.utils import formatter


class EventUtilsTest(unittest.TestCase):
    def testNotificationMessageFormaterGrades(self):
        # assume
        user_grade = {'node_id': 23348, 'private_comment': '', 'course_name': 'Hydraulika i hydrologia',
                      'grader': 'Szymon Firląg', 'grader_id': 92803, 'student_id': 1100392, 'public_comment': '',
                      'grade': {'symbol': '4,5', 'order_key': 2,
                                'name': 'cztery i pół', 'passes': True, 'decimal_value': '4.5'},
                      'last_changed': '2017-01-02 13:57:08'}

        # when
        notif, title, mess = formatter.format_user_grade(user_grade, 'create')

        # then
        self.assertEquals(notif, "Wpisano ocenę: 4.5 ze sprawdzianu (Hydraulika i hydrologia) - zalicza")
        self.assertEquals(title,
                          "Powiadomienie - Wpisano ocenę: 4.5 ze sprawdzianu (Hydraulika i hydrologia) - zalicza")

    def testNotificationMessageFormaterPoints(self):
        # assume -

        user_points = {'grader': 'Magdalena Skolimowska-Kulig', 'points': 10.0, 'comment': '',
                       'last_changed': '2017-01-03 23:10:35', 'student_id': 191953, 'grader_id': 1437,
                       'node_id': 26160, 'course_name': 'Elementy matematyki w ekonomii'}

        # when
        notif, title, mess = formatter.format_user_point(user_points, 'create')

        # then
        self.assertEquals(notif, "Wpisano punty: 10.0 ze sprawdzianu (Elementy matematyki w ekonomii)")
        self.assertEquals(title, "Powiadomienie - Wpisano punkty: 10.0 ze sprawdzianu (Elementy matematyki w ekonomii)")
