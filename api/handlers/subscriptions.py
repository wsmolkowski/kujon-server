# coding=UTF-8

from tornado import gen
from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators


class SubscriptionsHandler(ApiHandler):
    """
        displays user subscriptions, not casched in db, request go directly to usos api
    """

    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            subscriptions = yield self.usos_subscriptions()
            self.success(subscriptions)
        except Exception as ex:
            yield self.exc(ex)
