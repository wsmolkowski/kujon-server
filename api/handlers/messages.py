# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields, collections


class MessagesHandler(ApiHandler):
    """
        displays history of messages sent to client
    """

    async def _messages(self, pipeline):
        cursor = self.db[collections.MESSAGES].find(pipeline, {fields.MONGO_ID: 0,
                                                               "typ": 1,
                                                               "from": 1,
                                                               fields.CREATED_TIME: 1,
                                                               fields.JOB_MESSAGE: 1}
                                                    )
        return await cursor.to_list(None)

    @decorators.authenticated
    @web.asynchronous
    async def get(self):
        try:
            messages_doc = await self._messages({fields.USER_ID: self.getUserId()})
            self.success(messages_doc)
        except Exception as ex:
            await self.exc(ex)
