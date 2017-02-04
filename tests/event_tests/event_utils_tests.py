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

        user_points = {'grader': 'Jadwiga Płoszyńska', 'node_id': 8431, 'points': 0.0,
                       'student_id': 211158, 'last_changed': '2017-01-26 00:39:56', 'comment': '', 'grader_id': 8271, 'course_name': 'Maszyny elektryczne'}

        # when
        notif, title, mess = formatter.format_user_point(user_points, 'delete')

        # then
        self.assertEquals(notif, "Usunięto punty: 0.0 ze sprawdzianu (Maszyny elektryczne)")
        self.assertEquals(title, "Powiadomienie - Usunięto punkty: 0.0 ze sprawdzianu (Maszyny elektryczne)")
