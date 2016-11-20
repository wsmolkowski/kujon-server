# coding=utf-8
import unittest

from commons.mixins.MathMixin import MathMixin

GRADES_BY_TERM = {
    "data": [
        {
            "courses": [
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
                }
            ],
            "term_id": "2015/16-2"
        },
        {
            "courses": [
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
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
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
                            "value_description": "bardzo dobry",
                            "value_symbol": "5"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 22987,
                            "exam_session_number": 2,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 22987,
                            "exam_session_number": 1,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        }
                    ],
                    "term_id": "2014/15-2"
                }
            ],
            "term_id": "2014/15-2"
        },
        {
            "courses": [
                {
                    "course_id": "E-2IZ2-1005-s3",
                    "course_name": "Analiza i wizualizacja danych",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 18209,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 17893,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2014/15-1"
                },
                {
                    "course_id": "E-2IZ2-1002-s3",
                    "course_name": "Z\u0142o\u017cone struktury danych",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 18093,
                            "exam_session_number": 2,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 18093,
                            "exam_session_number": 1,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 17890,
                            "exam_session_number": 1,
                            "value_description": "dostateczny plus",
                            "value_symbol": "3,5"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 18206,
                            "exam_session_number": 1,
                            "value_description": "dostateczny plus",
                            "value_symbol": "3,5"
                        }
                    ],
                    "term_id": "2014/15-1"
                },
                {
                    "course_id": "E-2IZ2-1003-s3",
                    "course_name": "Symulacja komputerowa",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 17891,
                            "exam_session_number": 3,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 18207,
                            "exam_session_number": 3,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2014/15-1"
                },
                {
                    "course_id": "E-2IZ2-1004-s3",
                    "course_name": "Programowanie imperatywne, obiektowe i deklaratywne",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 18208,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 17892,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2014/15-1"
                },
                {
                    "course_id": "E-2IZ2-1001-s3",
                    "course_name": "Hurtownie danych",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 17889,
                            "exam_session_number": 2,
                            "value_description": "dostateczny plus",
                            "value_symbol": "3,5"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 18205,
                            "exam_session_number": 2,
                            "value_description": "dostateczny plus",
                            "value_symbol": "3,5"
                        }
                    ],
                    "term_id": "2014/15-1"
                }
            ],
            "term_id": "2014/15-1"
        },
        {
            "courses": [
                {
                    "course_id": "E-1IZ2-1001-s2",
                    "course_name": "Systemy mobilne",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16345,
                            "exam_session_number": 3,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16345,
                            "exam_session_number": 1,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16311,
                            "exam_session_number": 1,
                            "value_description": "dostateczny plus",
                            "value_symbol": "3,5"
                        }
                    ],
                    "term_id": "2013/14-2"
                },
                {
                    "course_id": "E-1IZ2-1002-s2",
                    "course_name": "Inteligentne us\u0142ugi informacyjne",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16294,
                            "exam_session_number": 2,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16294,
                            "exam_session_number": 1,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16346,
                            "exam_session_number": 1,
                            "value_description": "bardzo dobry",
                            "value_symbol": "5"
                        }
                    ],
                    "term_id": "2013/14-2"
                },
                {
                    "course_id": "E-1IZ2-1003-s2",
                    "course_name": "Modelowanie i analiza system\u00f3w informatycznych",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16312,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16341,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16347,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2013/14-2"
                },
                {
                    "course_id": "E-1IZ2-1004-s2",
                    "course_name": "Technologie obiektowe",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16348,
                            "exam_session_number": 2,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16348,
                            "exam_session_number": 3,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16348,
                            "exam_session_number": 1,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16431,
                            "exam_session_number": 2,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16431,
                            "exam_session_number": 1,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        }
                    ],
                    "term_id": "2013/14-2"
                },
                {
                    "course_id": "E-1IZ2-1005-s2",
                    "course_name": "J\u0119zyk angielski specjalistyczny",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 16324,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2013/14-2"
                }
            ],
            "term_id": "2013/14-2"
        },
        {
            "courses": [
                {
                    "course_id": "E-1IZ2-1003-s1",
                    "course_name": "Programowanie us\u0142ug sieciowych",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13183,
                            "exam_session_number": 1,
                            "value_description": "dobry plus",
                            "value_symbol": "4,5"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13227,
                            "exam_session_number": 1,
                            "value_description": "dobry plus",
                            "value_symbol": "4,5"
                        }
                    ],
                    "term_id": "2013/14-1"
                },
                {
                    "course_id": "E-1IZ2-1004-s1",
                    "course_name": "Projektowanie system\u00f3w wbudowanych",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13165,
                            "exam_session_number": 1,
                            "value_description": "dobry",
                            "value_symbol": "4"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13228,
                            "exam_session_number": 1,
                            "value_description": "dobry",
                            "value_symbol": "4"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13246,
                            "exam_session_number": 1,
                            "value_description": "dobry",
                            "value_symbol": "4"
                        }
                    ],
                    "term_id": "2013/14-1"
                },
                {
                    "course_id": "E-1IZ2-1005-s1",
                    "course_name": "Przedmiot humanistyczny",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13184,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2013/14-1"
                },
                {
                    "course_id": "E-1IZ2-1006-s1",
                    "course_name": "Zarz\u0105dzanie w\u0142asno\u015bci\u0105 intelektualn\u0105",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13185,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2013/14-1"
                },
                {
                    "course_id": "E-1IZ2-1001-s1",
                    "course_name": "Badania operacyjne w informatyce",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13182,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13207,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2013/14-1"
                },
                {
                    "course_id": "E-1IZ2-1002-s1",
                    "course_name": "Programowanie system\u00f3w rozproszonych",
                    "grades": [
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13226,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13245,
                            "exam_session_number": 2,
                            "value_description": "dobry plus",
                            "value_symbol": "4,5"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13245,
                            "exam_session_number": 1,
                            "value_description": "niedostateczny",
                            "value_symbol": "2"
                        },
                        {
                            "class_type": "Brak danych",
                            "exam_id": 13164,
                            "exam_session_number": 1,
                            "value_description": "dostateczny",
                            "value_symbol": "3"
                        }
                    ],
                    "term_id": "2013/14-1"
                }
            ],
            "term_id": "2013/14-1"
        }
    ],
    "status": "success"
}

GRADES = [
    {
        "class_type": "Brak danych",
        "exam_id": 13226,
        "exam_session_number": 1,
        "value_description": "dostateczny",
        "value_symbol": "3"
    },
    {
        "class_type": "Brak danych",
        "exam_id": 13245,
        "exam_session_number": 2,
        "value_description": "dobry plus",
        "value_symbol": "4,5"
    },
    {
        "class_type": "Brak danych",
        "exam_id": 13245,
        "exam_session_number": 1,
        "value_description": "niedostateczny",
        "value_symbol": "2"
    },
    {
        "class_type": "Brak danych",
        "exam_id": 13164,
        "exam_session_number": 1,
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
        result = mm._last_exam_session_number(GRADES)

        # then
        self.assertEqual(result['exam_session_number'], 2)
