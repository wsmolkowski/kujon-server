# coding=UTF-8

import logging
from datetime import date, timedelta, datetime

from api.handlers.base.api import ApiHandler
from commons import decorators
from commons.constants import fields, config, collections
from commons.errors import ApiError, CallerError


def _last_day_of_month(year, month):
    """ Work out the last day of the month """
    last_days = [31, 30, 29, 28, 27]
    for i in last_days:
        try:
            end = datetime(year, month, i)
        except ValueError:
            continue
        else:
            return end.date()
    return None


class TTUserApi(ApiHandler):

    async def api_ttmonth(self, given_date, lecturers_info=None):
        '''

        :param given_date: A date string, yyyy-mm-dd format
        :param lecturers_info: if True then extra data will be feched from USUS for each lecturer_id
        :param full_mobth: if None then next 7 days will be feched from USUS if true - full month
        :return:
        '''
        days = 7 # max usos value

        try:
            if isinstance(given_date, str):
                given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))

            first_day_of_month = date(given_date.year, given_date.month, 1)
            last_day_of_month = _last_day_of_month(given_date.year, given_date.month)

            second_week = first_day_of_month + timedelta(days=days)
            third_week = second_week + timedelta(days=days)
            fourth_week = third_week + timedelta(days=days)

            weeks = [first_day_of_month, second_week, third_week, fourth_week]

            if last_day_of_month.day > 28:
                fifth_week = fourth_week + timedelta(days=days)
                fifth_week_days = last_day_of_month.day - 28

        except Exception:
            return self.error("Podana data {0} jest w niepoprawnym formacie.".format(given_date))

        if await self.doRefresh():
            await self.db_remove(collections.TT, {fields.USER_ID: self.getUserId()})

        tt_doc = await self.db[collections.TT].find_one({fields.USER_ID: self.getUserId(),
                                                         fields.TT_STARTDATE: str(first_day_of_month)})
        if not tt_doc:

            tt_doc = dict()
            tt_doc['tts'] = list()
            tt_doc[fields.TT_STARTDATE] = str(first_day_of_month)
            tt_doc[fields.USER_ID] = self.getUserId()

            try:
                for week in weeks:
                    tt_response = await self.usosCall(
                        path='services/tt/user',
                        arguments={
                            'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
                            'start': week,
                            'days': days,
                        })

                    if not tt_response:
                        logging.debug("Brak wydarzeń w kalendarzu dla {0}".format(week))
                    else:
                        for elem in tt_response:
                            tt_doc['tts'].append(elem)

                if last_day_of_month.day > 28:
                    tt_response = await self.usosCall(
                        path='services/tt/user',
                        arguments={
                            'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
                            'start': fifth_week,
                            'days': fifth_week_days,
                        })
                    if not tt_response:
                        logging.debug("Brak wydarzeń w kalendarzu dla {0}".format(fifth_week))
                    else:
                        for elem in tt_response:
                            tt_doc['tts'].append(elem)

                if tt_doc['tts']:
                    for tt_data in tt_doc['tts']:
                        if tt_data['type'] == 'classgroup' or tt_data['type'] == 'classgroup2':
                            tt_data['type'] = 'zajęcia'
                        elif tt_data['type'] == 'exam':
                            tt_data['type'] = 'egzamin'

                    # insert only if exists
                    await self.db_insert(collections.TT, tt_doc)

            except Exception as ex:
                logging.debug(ex)
                raise ApiError("Bład podczas pobierania planu miesiąca dla użytkownika.")

        return tt_doc['tts']

    @decorators.authenticated
    async def get(self, given_date):

        lecturers_info = self.get_argument('lecturers_info', default=True)
        if lecturers_info == 'False':
            lecturers_info = False  # whatever is passed than convert to True

        try:
            tt_doc = await self.api_ttmonth(given_date, lecturers_info)
            self.success(tt_doc, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            self.error(message=ex, code=500)


class TTLecturerApi(ApiHandler):


    async def api_tt_lecturers(self, lecturer_id, given_date):
        '''

        :param given_date: A date string, yyyy-mm-dd format will be geting only current month
        :return: full month
        '''

        days = 7 # max usos value

        try:
            if isinstance(given_date, str):
                given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))

            first_day_of_month = date(given_date.year, given_date.month, 1)
            last_day_of_month = _last_day_of_month(given_date.year, given_date.month)

            second_week = first_day_of_month + timedelta(days=days)
            third_week = second_week + timedelta(days=days)
            fourth_week = third_week + timedelta(days=days)

            if last_day_of_month.day > 28:
                fifth_week = fourth_week + timedelta(days=days)
                fifth_week_days = last_day_of_month.day - 28

        except Exception as ex:
            raise Exception("Podana data {0} jest w niepoprawnym formacie.".format(given_date))

        if await self.doRefresh():
            await self.db_remove(collections.TT_LECTURERS, {fields.USOS_USER_ID: lecturer_id,
                                                            fields.USOS_ID: self.getUsosId()})

        tt_doc = await self.db[collections.TT_LECTURERS].find_one({fields.USOS_USER_ID: lecturer_id,
                                                                   fields.USOS_ID: self.getUsosId(),
                                                                   fields.TT_STARTDATE: str(first_day_of_month)})
        if not tt_doc:

            tt_doc = dict()
            tt_doc['tts'] = list()
            tt_doc[fields.TT_STARTDATE] = str(first_day_of_month)
            tt_doc[fields.USOS_USER_ID] = lecturer_id

            try:
                for week in [first_day_of_month, second_week, third_week, fourth_week]:

                    tt_response = await self.usosCall(
                        path='services/tt/staff',
                        arguments={
                            'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number',
                            'start': week,
                            'days': 7,
                            'user_id': int(lecturer_id)
                        })

                    if not tt_response:
                        logging.debug("Brak wydarzeń w kalendarzu dla {0}".format(week))
                    else:
                        for elem in tt_response:
                            tt_doc['tts'].append(elem)

                if last_day_of_month.day > 28:
                    tt_response = await self.usosCall(
                        path='services/tt/staff',
                        arguments={
                            'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number',
                            'start': fifth_week,
                            'days': fifth_week_days,
                            'user_id': lecturer_id
                        })
                    if not tt_response:
                        logging.debug("Brak wydarzeń w kalendarzu dla {0}".format(fifth_week))
                    else:
                        for elem in tt_response:
                            tt_doc['tts'].append(elem)

                if tt_doc['tts']:
                    for tt_data in tt_doc['tts']:
                        if tt_data['type'] == 'classgroup' or tt_data['type'] == 'classgroup2':
                            tt_data['type'] = 'zajęcia'
                        elif tt_data['type'] == 'exam':
                            tt_data['type'] = 'egzamin'

                    await self.db_insert(collections.TT_LECTURERS, tt_doc)

            except Exception:
                raise ApiError("Bład podczas pobierania planu dla wykładowcy.")

        return tt_doc['tts']


    @decorators.authenticated
    async def get(self, lecturer_id, given_date):

        try:
            if not lecturer_id or not given_date:
                self.error("Niepoprawne parametry wywołania.")
                return
            tt_doc = await self.api_tt_lecturers(lecturer_id, given_date)
            return self.success(tt_doc, cache_age=config.SECONDS_1WEEK)
        except Exception as ex:
            await self.exc(ex)


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
            return self.error("Podana data {0} jest w niepoprawnym formacie.".format(given_date))

        if await self.doRefresh():
            await self.db_remove(collections.TT, {fields.USER_ID: self.getUserId()})

        tt_doc = await self.db[collections.TT].find_one({fields.USER_ID: self.getUserId(),
                                                         fields.TT_STARTDATE: str(monday)})
        if not tt_doc:
            tt_response = await self.usosCall(
                path='services/tt/user',
                arguments={
                    'fields': 'start_time|end_time|name|type|course_id|course_name|building_name|room_number|group_number|lecturer_ids',
                    'start': given_date,
                    'days': days
                })

            if not tt_response:
                raise ApiError("Brak wydarzeń w kalendarzu dla {0}".format(given_date))

            tt_doc = dict()
            tt_doc[fields.TT_STARTDATE] = str(given_date)
            tt_doc['tts'] = tt_response
            tt_doc[fields.USER_ID] = self.getUserId()

            # await self.db_insert(collections.TT, tt_doc)

        for tt_data in tt_doc['tts']:
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
    async def get(self, given_date):

        lecturers_info = self.get_argument('lecturers_info', default=True)
        if lecturers_info == 'False':
            lecturers_info = False  # whatever is passed than convert to True

        days = self.get_argument('days', default=None)

        try:
            tt_doc = await self.api_tt(given_date, lecturers_info, days)
            self.success(tt_doc, cache_age=config.SECONDS_1WEEK)
        except (ApiError, CallerError) as ex:
            logging.debug(ex)
            self.success(list())
        except Exception as ex:
            await self.exc(ex)

