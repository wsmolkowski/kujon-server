# coding=utf-8
import unittest

from commons.mixins.MathMixin import MathMixin

GRADES_BY_TERM = [
    {
        "course_id": "E-2IZ2-1007-s4",
        "course_name": "Statystyka w informatyce",
        "grades": [
            {
                "class_type": "Projekt",
                "exam_id": 36687,
                "exam_session_number": 1,
                "value_description": "dostateczny plus",
                "value_symbol": "3,5"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 36625,
                "exam_session_number": 1,
                "value_description": "dostateczny",
                "value_symbol": "3"
            }
        ],
        "term_id": "2015/16-2"
    },
    {
        "course_id": "E-2IZ2-1003-s4",
        "course_name": "Seminarium dyplomowe",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 36684,
                "exam_session_number": 1,
                "value_description": "bardzo dobry",
                "value_symbol": "5"
            }
        ],
        "term_id": "2015/16-2"
    },
    {
        "course_id": "E-2IZ2-1004-s4",
        "course_name": "Praca dyplomowa",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 36691,
                "exam_session_number": 1,
                "value_description": "bardzo dobry",
                "value_symbol": "5"
            }
        ],
        "term_id": "2015/16-2"
    },
    {
        "course_id": "E-2IZ2-1006-s4",
        "course_name": "Niezawodno\u015b\u0107 system\u00f3w komputerowych",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 36624,
                "exam_session_number": 1,
                "value_description": "dostateczny",
                "value_symbol": "3"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 36686,
                "exam_session_number": 1,
                "value_description": "dostateczny",
                "value_symbol": "3"
            }
        ],
        "term_id": "2015/16-2"
    },
    {
        "course_id": "E-2IZ2-1006-s4",
        "course_name": "Niezawodno\u015b\u0107 system\u00f3w komputerowych",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 22677,
                "exam_session_number": 1,
                "value_description": "dostateczny",
                "value_symbol": "3"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 22676,
                "exam_session_number": 1,
                "value_description": "dostateczny",
                "value_symbol": "3"
            }
        ],
        "term_id": "2014/15-2"
    },
    {
        "course_id": "E-2IZ2-1005-s4",
        "course_name": "Procesory sygna\u0142owe",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 22672,
                "exam_session_number": 1,
                "value_description": "dostateczny plus",
                "value_symbol": "3,5"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 22674,
                "exam_session_number": 1,
                "value_description": "dostateczny plus",
                "value_symbol": "3,5"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 22673,
                "exam_session_number": 1,
                "value_description": "dostateczny plus",
                "value_symbol": "3,5"
            }
        ],
        "term_id": "2014/15-2"
    },
    {
        "course_id": "E-2IZ2-1003-s4",
        "course_name": "Seminarium dyplomowe",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 25502,
                "exam_session_number": 1,
                "value_description": "dostateczny plus",
                "value_symbol": "3,5"
            }
        ],
        "term_id": "2014/15-2"
    },
    {
        "course_id": "E-1IZ2-1004-s2",
        "course_name": "Technologie obiektowe",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 23472,
                "exam_session_number": 1,
                "value_description": "dostateczny",
                "value_symbol": "3"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 25498,
                "exam_session_number": 2,
                "value_description": "niedostateczny",
                "value_symbol": "2"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 25498,
                "exam_session_number": 3,
                "value_description": "dostateczny",
                "value_symbol": "3"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 25498,
                "exam_session_number": 1,
                "value_description": "bardzo dobry (5,0)",
                "value_symbol": "5,0 (bdb)"
            }
        ],
        "term_id": "2014/15-2"
    },
    {
        "course_id": "E-1IZ2-1002-s2",
        "course_name": "Inteligentne us\u0142ugi informacyjne",
        "grades": [
            {
                "class_type": "Brak danych",
                "exam_id": 25496,
                "exam_session_number": 1,
                "value_description": "plus dobry (4,5)",
                "value_symbol": "4,5 (+db)"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 22987,
                "exam_session_number": 2,
                "value_description": "plus dostateczny (3,5)",
                "value_symbol": "3,5 (+dst)"
            },
            {
                "class_type": "Brak danych",
                "exam_id": 22987,
                "exam_session_number": 1,
                "value_description": "bardzo dobry (5,0)",
                "value_symbol": "5,0 (bdb)"
            }
        ],
        "term_id": "2014/15-2"
    }
]

GRADES = [
    {
        "class_type": "Brak danych",
        "exam_id": 1,
        "exam_session_number": 1,
        "value_description": "dostateczny",
        "value_symbol": "3"
    },
    {
        "class_type": "Brak danych",
        "exam_id": 2,
        "exam_session_number": 2,
        "value_description": "dobry plus",
        "value_symbol": "4,5"
    },
    {
        "class_type": "Brak danych",
        "exam_id": 3,
        "exam_session_number": 1,
        "value_description": "niedostateczny",
        "value_symbol": "2"
    },
    {
        "class_type": "Brak danych",
        "exam_id": 4,
        "exam_session_number": 3,
        "value_description": "dostateczny",
        "value_symbol": "3"
    }
]


class MathMixinTest(unittest.TestCase):
    def testMathAverageGrades(self):
        # assume
        mm = MathMixin()

        # when
        result = mm._math_average_grades(GRADES_BY_TERM)

        # then
        self.assertIsNotNone(result)

    def testLastExamSessionNumber(self):
        # assume
        mm = MathMixin()

        # when
        result = mm._get_only_final_grades(GRADES)

        # then
        self.assertEqual(result[0]['exam_session_number'], 3)
