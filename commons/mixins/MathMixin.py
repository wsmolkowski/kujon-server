# coding=UTF-8

import logging

AVERAGE_GRADE_ROUND = 2


class MathMixin(object):
    def _last_exam_session_number(self, grades):
        max_exam_session_number = None

        for grade in grades:
            if 'exam_session_number' not in grade:
                continue

            if not max_exam_session_number:
                max_exam_session_number = grade
                continue

            if int(grade['exam_session_number']) > max_exam_session_number['exam_session_number']:
                max_exam_session_number = grade

        return max_exam_session_number

    def _math_average_grades(self, courses_lists):
        value_symbols = list()

        for course in courses_lists:
            if 'grades' not in course:
                continue

            grade = self._last_exam_session_number(course['grades'])

            if 'value_symbol' not in grade:
                continue
            try:
                value_symbol = float(grade['value_symbol'])
                value_symbols.append(value_symbol)
            except ValueError:
                continue

        if not value_symbols:
            return

        try:
            return round(sum(value_symbols)/len(value_symbols), AVERAGE_GRADE_ROUND)
        except Exception as ex:
            logging.exception(ex)
            return