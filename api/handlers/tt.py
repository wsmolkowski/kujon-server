# coding=UTF-8

import logging
from datetime import date, timedelta

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators, constants
from commons.UsosCaller import UsosCaller
from commons.errors import ApiError, CallerError


class TTApi(ApiHandler):
    async def _lecturers_info(self, lecturer_ids):
        lecturer_keys = ['id', 'first_name', 'last_name', 'titles']

        lecturers_infos = list()
        for lecturer_id in lecturer_ids:
            try:
                lecturer_info = await self.api_user_info(lecturer_id)
                if lecturers_infos:
                    lecturer_info = dict([(key, lecturer_info[key]) for key in lecturer_keys])
                    lecturers_infos.append(lecturer_info)

            except Exception as ex:
                await self.exc(ex, finish=False)

        return lecturers_infos

    async def api_tt(self, given_date, lecturers_info=None, days=None):
        '''

        :param given_date: A date string, yyyy-mm-dd format
        :param lecturers_info: if True then extra data will be feched from USUS for each lecturer_id
        :param days: if None then data for next 7 days will be feched from USUS
        :return:
        '''

        if not days:
            days = '7'

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
                    'days': days
                })

            if not tt_response:
                raise ApiError("Brak wydarzeń w kalendarzu dla {0}".format(given_date))

            tt_doc = dict()
            tt_doc[constants.TT_STARTDATE] = str(given_date)
            tt_doc['tts'] = tt_response
            tt_doc[constants.USER_ID] = self.getUserId()

            # await self.db_insert(constants.COLLECTION_TT, tt_doc)

        for tt_data in tt_doc['tts']:
            tt_data['name'] = tt_data['name']['pl']
            tt_data[constants.COURSE_NAME] = tt_data[constants.COURSE_NAME]['pl']
            tt_data['building_name'] = tt_data['building_name']['pl']
            if tt_data['type'] == 'classgroup':
                tt_data['type'] = 'zajęcia'
            elif tt_data['type'] == 'exam':
                tt_data['type'] = 'egzamin'

            if 'lecturer_ids' in tt_data:
                if lecturers_info:
                    tt_data['lecturers'] = await self._lecturers_info(tt_data['lecturer_ids'])
                else:
                    tt_data['lecturers'] = len(tt_data['lecturer_ids'])
            else:
                tt_data['lecturers'] = list()

        return tt_doc['tts']

    @decorators.authenticated
    @web.asynchronous
    async def get(self, given_date):

        lecturers_info = self.get_argument('lecturers_info', default=True)
        if lecturers_info == 'False':
            lecturers_info = False  # whatever is passed than convert to True

        days = self.get_argument('days', default=None)

        try:
            tt_doc = await self.api_tt(given_date, lecturers_info, days)
            self.success(tt_doc, cache_age=constants.SECONDS_1WEEK)
        except (ApiError, CallerError) as ex:
            logging.debug(ex)
            self.success(list())
        except Exception as ex:
            await self.exc(ex)
