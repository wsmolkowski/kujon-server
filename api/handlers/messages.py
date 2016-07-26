# coding=UTF-8

from tornado import gen
from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class MessagesHandler(ApiHandler):
    """
        displays history of messages sent to client
    """

    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            messages_doc = yield self.db_messages({constants.USER_ID: self.getUserId(), constants.MONGO_ID: False})
            self.success(messages_doc)
        except Exception as ex:
            yield self.exc(ex)
