# coding=UTF-8

import logging
from datetime import date, timedelta

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators, constants
from commons.UsosCaller import UsosCaller
from commons.errors import ApiError, CallerError


class TTApi(ApiHandler):
    async def _lecturers_info(self, tt):
        lecturer_keys = ['id', 'first_name', 'last_name', 'titles']

        lecturers_infos = list()
        for lecturer_id in tt['lecturer_ids']:
            try:
                lecturer_info = await self.api_user_info(lecturer_id)
                lecturer_info = dict([(key, lecturer_info[key]) for key in lecturer_keys])
                lecturers_infos.append(lecturer_info)

            except Exception as ex:
                logging.debug(ex)  # exception save in self.api_user_info

        return lecturers_infos

    async def api_tt(self, given_date):

        try:
            if isinstance(given_date, str):
                given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))
            monday = given_date - timedelta(days=(given_date.weekday()) % 7)
        except Exception:
            raise ApiError("Podana data {0} jest w niepoprawnym formacie.".format(given_date))

        if self.do_refresh():
            await self.db_remove(constants.COLLECTION_TT, {constants.USER_ID: self.getUserId()})

        tt_doc = await self.db[constants.COLLECTION_TT].find_one({constants.USER_ID: self.getUserId(),
                                                                  constants.TT_STARTDATE: str(monday)})
        if not tt_doc:
            tt_response = await UsosCaller(self._context).call(
                path='services/tt/user',
                arguments={
                    'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
                    'start': given_date,
                    'days': '7'
                })

            if not tt_response:
                raise ApiError("Brak wydarzeń w kalendarzu dla {0}".format(given_date))

            tt_doc = dict()
            tt_doc[constants.TT_STARTDATE] = str(given_date)
            tt_doc['tts'] = tt_response
            tt_doc[constants.USER_ID] = self.get_current_user()[constants.MONGO_ID]

            await self.db_insert(constants.COLLECTION_TT, tt_doc)

        for t in tt_doc['tts']:
            t['name'] = t['name']['pl']
            t[constants.COURSE_NAME] = t[constants.COURSE_NAME]['pl']
            t['building_name'] = t['building_name']['pl']
            if t['type'] == 'classgroup':
                t['type'] = 'zajęcia'
            elif t['type'] == 'exam':
                t['type'] = 'egzamin'

        # add lecturer information  - API errors
        # try:
        #     if 'tts' in tt_doc:
        #         lecturers_infos = list()
        #         for tt in tt_doc['tts']:
        #             lecturers_infos.append(self._lecturers_info(tt))
        #         tt_lecturers = await gen.multi(lecturers_infos)
        #         tt_lecturers = self.filterNone(tt_lecturers)
        #     else:
        #         tt_lecturers = list()
        # except Exception as ex:
        #     await self.exc(ex, finish=False)
        #     tt_lecturers = list()

        tt_doc['lecturers'] = list()

        return tt_doc

    @decorators.authenticated
    @web.asynchronous
    async def get(self, given_date):

        try:
            tt_doc = await self.api_tt(given_date)
            self.success(tt_doc, cache_age=constants.SECONDS_1WEEK)
        except (ApiError, CallerError) as ex:
            logging.debug(ex)
            self.success(dict())
        except Exception as ex:
            await self.exc(ex)
