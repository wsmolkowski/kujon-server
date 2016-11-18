# coding=UTF-8

import logging

AVERAGE_GRADE_ROUND = 1


class MathMixin(object):
    def _math_average_grades(self, courses_lists):
        value_symbols = list()

        for course in courses_lists:
            if 'grades' not in course:
                continue

            for grade in course['grades']:
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