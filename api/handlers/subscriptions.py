# coding=UTF-8

from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators, constants
from commons.UsosCaller import UsosCaller


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
                constants.USER_ID: self.getUserId(),
                constants.USOS_ID: self.getUsosId(),
                constants.MONGO_ID: False
            })

            if subscriptions:
                subscriptions_doc['subscriptions'] = subscriptions

            usos_subscriptions = await UsosCaller(self._context).call(path='services/events/subscriptions')
            if not usos_subscriptions:
                usos_subscriptions = dict()

            if usos_subscriptions:
                subscriptions_doc['usos_subscriptions'] = usos_subscriptions

            self.success(subscriptions_doc)
        except Exception as ex:
            await self.exc(ex)
