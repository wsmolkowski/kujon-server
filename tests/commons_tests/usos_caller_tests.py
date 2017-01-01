# coding=utf-8
import unittest

from commons.UsosCaller import strip_english_language


class UsosCallerTest(unittest.TestCase):
    def testStripENLanguage(self):
        # assume
        input_json = {
            "course_id": "2500-KF-PB-10",
            "course_name": "Psychologia tw\u00f3rczo\u015bci",
            "grades": [
                {
                    "class_type": {
                        "en": "Lecture",
                        "pl": "Wyk\u0142ad"
                    },
                    "exam_id": 393858,
                    "exam_session_number": 1,
                    "value_description": "nie klasyfikowany",
                    "value_symbol": "NK"
                }
            ],
            "term_id": "2015L"
        }

        # when
        result = strip_english_language(input_json)

        # then
        print(result)
        self.assertIsNotNone(result)
