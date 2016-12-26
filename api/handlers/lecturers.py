# coding=UTF-8

from api.handlers.base import ApiHandler
from commons import decorators
from commons.errors import ApiError
from commons.constants import fields, config


class LecturersApi(ApiHandler):
    async def api_lecturers(self):
        courses_editions = await self.api_courses_editions()
        if not courses_editions:
            raise ApiError("Poczekaj szukamy nauczycieli.")

        result = list()
        for term, courses in list(courses_editions[fields.COURSE_EDITIONS].items()):
            for course in courses:
                for lecturer in course[fields.LECTURERS]:
                    if lecturer not in result:
                        result.append(lecturer)
        result = sorted(result, key=lambda k: k['last_name'])
        return result

    @decorators.authenticated
    async def get(self):

        try:
            lecturers_doc = await self.api_lecturers()
            if not lecturers_doc:
                self.error("Brak informacji o Twoich wykładowcach.")
            else:
                self.success(lecturers_doc, cache_age=config.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)


class LecturerByIdApi(ApiHandler):
    @decorators.authenticated
    async def get(self, user_info_id):

        try:
            user_info_doc = await self.api_user_info(user_info_id)  # lecturer
            if not user_info_doc:
                self.error("Brak informacji o wykładowcy {0}".format(user_info_id), code=404)
            else:
                self.success(user_info_doc, cache_age=config.SECONDS_2MONTHS)
        except Exception as ex:
            await self.exc(ex)
