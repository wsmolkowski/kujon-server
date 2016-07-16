# coding=UTF-8

from bson import ObjectId
from tornado import gen
from tornado import web

from api.handlers.base import DaoMixin
from commons import decorators, constants
from commons.UsosCaller import UsosCaller


class SubscriptionsHandler(DaoMixin):
    """
        displays user subscriptions, not casched in db, request go directly to usos api
    """

    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            subscriptions_doc = dict()
            subscriptions = yield self.db_subscriptions({
                constants.USER_ID: ObjectId(self.get_current_user()[constants.MONGO_ID]),
                constants.USOS_ID: self.get_current_user()[constants.USOS_ID]
            })

            if subscriptions:
                subscriptions_doc['subscriptions'] = subscriptions

            usos_subscriptions = yield UsosCaller(self._context).call(path='services/events/subscriptions')
            if not usos_subscriptions:
                usos_subscriptions = dict()

            if usos_subscriptions:
                subscriptions_doc['usos_subscriptions'] = usos_subscriptions

            self.success(subscriptions_doc)
        except Exception as ex:
            yield self.exc(ex)
