# coding=UTF-8

from tornado import gen
from tornado import web

from base import ApiHandler
from commons import constants, decorators

LIMIT_FIELDS = ('class_type_id', 'course_unit_id', constants.TERM_ID, 'lecturers')


class GroupsApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self, course):

        try:
            user_info = yield self.api_user_info()

            programmes = []
            for program in user_info['student_programmes']:
                program_id = program['programme']['id']
                result = yield self.api_programme(program_id, finish=False)
                programmes.append(result)

            if not programmes:
                self.error("Poczekaj szukamy danych o Twoich grupach.")
            else:
                self.success(programmes, cache_age=constants.SECONDS_1MONTH)

        except Exception, ex:
            yield self.exc(ex)
