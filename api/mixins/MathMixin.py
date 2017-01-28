# coding=UTF-8

import logging
import re

from commons.constants import fields

AVERAGE_GRADE_ROUND = 2
DEFAULT_NEGATIVE_GRADE = "2.0"
NEGATIVE_GRADES_DESCRIPTIONS = ["NK", "NZAL", "NB", "BO", "NIEOBECNY", "N.P.", "niekwalifikowany"]
POSITIVE_GRADES_DESCRIPTIONS = ["ZAL", "ZA", "ZAL.", "ZWOL LEK.", "ZW-LEK", "ZWOL", "ZW", "ZWL", "-"]


class MathMixin(object):
    @staticmethod
    def _get_only_final_grades(grades):
        final_grades = list()

        for grade in grades:
            if not final_grades:
                final_grades.append(grade)
                continue

            found = 0
            for final_grade in final_grades:
                if grade[fields.CLASS_TYPE] is final_grade[fields.CLASS_TYPE]:
                    if int(grade[fields.EXAM_SESSION_NUMBER]) > int(final_grade[fields.EXAM_SESSION_NUMBER]):
                        final_grades.remove(final_grade)
                        final_grades.append(grade)
                    found = 1
            if found == 0:
                final_grades.append(grade)

        return final_grades

    def _math_average_grades(self, courses_lists):
        value_symbols = list()

        for course in courses_lists:
            if fields.GRADES not in course:
                continue

            grades = self._get_only_final_grades(course[fields.GRADES])
            for grade in grades:
                grade_value = None
                if fields.VALUE_SYMBOL not in grade or not grade[fields.VALUE_SYMBOL]:
                    continue
                try:

                    grade_value = grade[fields.VALUE_SYMBOL].replace(',', '.')

                    if grade_value.upper() in NEGATIVE_GRADES_DESCRIPTIONS:
                        grade_value = DEFAULT_NEGATIVE_GRADE

                    if grade_value.upper() in POSITIVE_GRADES_DESCRIPTIONS:
                        continue

                    # get only integer &decimal numbers somtimes grades are in such format "5,0 (bdb)"
                    tmp = re.search('(?:\d*\.)?\d+', grade_value)
                    if tmp:
                        grade_value = tmp.group(0)

                    value_symbols.append(float(grade_value))

                except (ValueError, TypeError):
                    logging.error("Liczenie średniej - nieprawidłowa ocena: %s ", grade_value)
                    continue

        if not value_symbols:
            return

        try:
            avg = str(float(round(sum(value_symbols) / len(value_symbols), AVERAGE_GRADE_ROUND)))
            logging.debug("Średnia: %s z %s ocen: %s", avg, len(value_symbols), value_symbols)
            return avg
        except Exception as ex:
            logging.exception(ex)
            return
