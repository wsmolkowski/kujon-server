# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators
from commons.constants import fields


class SubscriptionsHandler(ApiHandler):
    """
        displays user subscriptions, not casched in db, request go directly to usos api
    """

    @decorators.authenticated
    @web.asynchronous
    async def get(self):
        try:
            subscriptions_doc = dict()
            subscriptions = await self.db_subscriptions({
                fields.USER_ID: self.getUserId(),
                fields.USOS_ID: self.getUsosId(),
                fields.MONGO_ID: False
            })

            if subscriptions:
                subscriptions_doc['subscriptions'] = subscriptions

            usos_subscriptions = await self.usosCall(path='services/events/subscriptions')
            if not usos_subscriptions:
                usos_subscriptions = dict()

            if usos_subscriptions:
                subscriptions_doc['usos_subscriptions'] = usos_subscriptions

            self.success(subscriptions_doc)
        except Exception as ex:
            await self.exc(ex)
