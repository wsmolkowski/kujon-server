# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields


class SettingsHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self):
        try:
            self.success(data=self.getUserSettings())
        except Exception as ex:
            await self.exc(ex)


class EventEnableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            # json_settings = escape.json_decode(self.request.body.decode())
            await self.db_settings_update(self.getUserId(), fields.EVENT_ENABLE, True)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class EventDisableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), fields.EVENT_ENABLE, False)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class GoogleCallendarEnableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), fields.GOOGLE_CALLENDAR_ENABLE, True)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class GoogleCallendarDisableHandler(ApiHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), fields.GOOGLE_CALLENDAR_ENABLE, False)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)
