# coding=UTF-8


from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, config


class CourseEditionApi(ApiHandler):
    @decorators.authenticated
    async def get(self, course_id, term_id):

        try:
            course_doc = await self.api_course_term(course_id, term_id)
            if course_doc:
                self.success(course_doc, cache_age=config.SECONDS_1WEEK)
            else:
                self.error('Nie znaleziono informacji o danej edycji kursu.', code=404)
        except Exception as ex:
            await self.exc(ex)


class CoursesApi(ApiHandler):
    @decorators.authenticated
    async def get(self, course_id):

        try:
            course_doc = await self.api_course(course_id)
            if course_doc:
                self.success(course_doc, cache_age=config.SECONDS_1MONTH)
            else:
                self.error('Nie znaleziono informacji o danym kursie.', code=404)
        except Exception as ex:
            await self.exc(ex)


class CoursesEditionsApi(ApiHandler):
    @decorators.authenticated
    async def get(self):

        try:
            courses = await self.api_courses(course_fields=[fields.COURSE_ID, fields.COURSE_NAME, fields.TERM_ID])
            self.success(courses, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)


class CoursesEditionsByTermApi(ApiHandler):
    @decorators.authenticated
    async def get(self):

        try:
            courses = await self.api_courses_by_term(
                course_fields=[fields.COURSE_ID, fields.COURSE_NAME, fields.TERM_ID])
            self.success(courses, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)
