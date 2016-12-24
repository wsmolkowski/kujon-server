# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields


class MessagesHandler(ApiHandler):
    """
        displays history of messages sent to client
    """

    @decorators.authenticated
    @web.asynchronous
    async def get(self):
        try:
            messages_doc = await self.db_messages({fields.USER_ID: self.getUserId()})
            self.success(messages_doc)
        except Exception as ex:
            await self.exc(ex)
