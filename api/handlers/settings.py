# coding=UTF-8

from tornado import web

from api.handlers.base.base import BaseHandler
from commons import decorators
from commons.constants import fields


class SettingsHandler(BaseHandler):
    @decorators.authenticated
    @web.asynchronous
    async def get(self):
        try:
            self.success(data=self.getUserSettings())
        except Exception as ex:
            await self.exc(ex)


class EventEnableHandler(BaseHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            # json_settings = escape.json_decode(self.request.body.decode())
            await self.db_settings_update(self.getUserId(), fields.EVENT_ENABLE, True)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class EventDisableHandler(BaseHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), fields.EVENT_ENABLE, False)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class GoogleCallendarEnableHandler(BaseHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), fields.GOOGLE_CALLENDAR_ENABLE, True)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)


class GoogleCallendarDisableHandler(BaseHandler):
    @decorators.authenticated
    @web.asynchronous
    async def post(self):

        try:
            await self.db_settings_update(self.getUserId(), fields.GOOGLE_CALLENDAR_ENABLE, False)
            self.success(data='user setting set properly')
        except Exception as ex:
            await self.exc(ex)
