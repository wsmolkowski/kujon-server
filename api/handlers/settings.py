# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators


class SettingsHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self):
        try:
            settings = await self.db_settings(self.getUserId())

            if not settings:
                await self.db_settings_update(self.getUserId(), 'event_enable', False)
                await self.db_settings_update(self.getUserId(), 'google_callendar_enable', False)

                settings = await self.db_settings(self.getUserId())

            self.success(data=settings)
        except Exception as ex:
            await self.exc(ex)


class EventEnableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            # json_settings = escape.json_decode(self.request.body.decode())
            await self.db_settings_update(self.getUserId(), 'event_enable', True)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class EventDisableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), 'event_enable', False)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class GoogleCallendarEnableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), 'google_callendar_enable', True)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class GoogleCallendarDisableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), 'google_callendar_enable', False)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)
