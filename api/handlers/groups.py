# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import constants, decorators
from commons.errors import CallerError

LIMIT_FIELDS = ('class_type_id', 'course_unit_id', constants.TERM_ID, 'lecturers')


class GroupsApi(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self, course):

        try:
            user_info = await self.api_user_usos_info()

            if not user_info:
                raise CallerError("Wystąpił problem z dostępem do usług USOS API. Spróbuj ponownie za chwilę.")

            programmes = []
            for program in user_info['student_programmes']:
                program_id = program['programme']['id']
                result = await self.api_programme(program_id, finish=False)
                programmes.append(result)

            if not programmes:
                self.error("Poczekaj szukamy danych o Twoich grupach.")
            else:
                self.success(programmes, cache_age=constants.SECONDS_1MONTH)

        except Exception as ex:
            await self.exc(ex)
