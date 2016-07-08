# coding=UTF-8

from bson import ObjectId
from tornado import gen
from tornado import web

from api.handlers.base import ApiHandler
from commons import decorators, constants


class SubscriptionsHandler(ApiHandler):
    """
        displays user subscriptions, not casched in db, request go directly to usos api
    """

    @decorators.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            subscriptions_doc = yield self.db[constants.COLLECTION_SUBSCRIPTION].find({
                constants.USER_ID: ObjectId(self.get_current_user()[constants.MONGO_ID]),
                constants.USOS_ID: self.get_current_user()[constants.USOS_ID]
            })

            if not subscriptions_doc:
                subscriptions_doc = dict()
            subscriptions = yield self.usos_subscriptions()
            subscriptions_doc['usos_subscriptions'] = subscriptions

            self.success(subscriptions_doc)
        except Exception as ex:
            yield self.exc(ex)
