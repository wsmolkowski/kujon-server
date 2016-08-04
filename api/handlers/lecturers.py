# coding=UTF-8

import tornado.web

from api.handlers.base import ApiHandler
from commons import constants, decorators


class LecturersApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self):

        try:
            lecturers_doc = await self.api_lecturers()
            if not lecturers_doc:
                self.error("Brak informacji o Twoich wykładowcach.")
            else:
                self.success(lecturers_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)


class LecturerByIdApi(ApiHandler):
    async def api_lecturer(self, user_info_id):
        user_info = await self.api_user_info(user_info_id)
        return user_info

    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self, user_info_id):

        try:
            user_info_doc = await self.api_lecturer(user_info_id)
            if not user_info_doc:
                self.error("Brak informacji o tym wykładowcy.", code=404)
            else:
                self.success(user_info_doc, cache_age=constants.SECONDS_2MONTHS)
        except Exception as ex:
            await self.exc(ex)
