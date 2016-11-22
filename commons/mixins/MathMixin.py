# coding=UTF-8

import logging

from commons import constants

AVERAGE_GRADE_ROUND = 2
DEFAULT_NEGATIVE_GRADE = 2


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
                if grade[constants.CLASS_TYPE] is final_grade[constants.CLASS_TYPE]:
                    if int(grade[constants.EXAM_SESSION_NUMBER]) > int(final_grade[constants.EXAM_SESSION_NUMBER]):
                        final_grades.remove(final_grade)
                        final_grades.append(grade)
                    found = 1
            if found == 0:
                final_grades.append(grade)

        return final_grades

    def _math_average_grades(self, courses_lists):
        value_symbols = list()

        for course in courses_lists:
            if constants.GRADES not in course:
                continue

            grades = self._get_only_final_grades(course[constants.GRADES])
            for grade in grades:
                if constants.VALUE_SYMBOL not in grade or not grade[constants.VALUE_SYMBOL]:
                    continue
                try:
                    grade_value = grade[constants.VALUE_SYMBOL].replace(',', '.')
                    if 'NZAL' in grade_value or 'NK' in grade_value:
                        grade_value = DEFAULT_NEGATIVE_GRADE

                    value_symbols.append(float(grade_value))
                except ValueError:
                    continue

        if not value_symbols:
            return

        try:
            logging.debug(value_symbols)
            return str(float(round(sum(value_symbols) / len(value_symbols), AVERAGE_GRADE_ROUND)))
        except Exception as ex:
            logging.exception(ex)
            return

