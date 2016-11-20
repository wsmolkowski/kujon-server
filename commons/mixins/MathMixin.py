# coding=UTF-8

import logging

AVERAGE_GRADE_ROUND = 2


class MathMixin(object):
    def _get_only_final_grades(self, grades):
        final_grades = list()
        found = int()

        for grade in grades:
            if not final_grades:
                final_grades.append(grade)
                continue

            found = 0
            for final_grade in final_grades:
                if grade['class_type'] is final_grade['class_type']:
                    if int(grade['exam_session_number']) > int(final_grade['exam_session_number']):
                        final_grades.remove(final_grade)
                        final_grades.append(grade)
                        found = 1
            if found == 0:
                final_grades.append(grade)

        return final_grades

    def _math_average_grades(self, courses_lists):
        value_symbols = list()

        for course in courses_lists:
            if 'grades' not in course:
                continue

            grades = self._get_only_final_grades(course['grades'])
            for grade in grades:
                if 'value_symbol' not in grade:
                    continue
                try:
                    value_symbol = float(grade['value_symbol'].replace(",", "."))
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