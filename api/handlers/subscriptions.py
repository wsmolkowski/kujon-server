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
            pipeline = {constants.USER_ID: ObjectId(self.get_current_user()[constants.MONGO_ID]),
                        constants.USOS_ID: self.get_current_user()[constants.USOS_ID]
                        }

            if self.do_refresh():
                yield self.db_remove(constants.COLLECTION_SUBSCRIPTION, pipeline)

            subscriptions_doc = yield self.db[constants.COLLECTION_SUBSCRIPTION].find(pipeline)

            if not subscriptions_doc:
                subscriptions_doc = yield self.usos_subscriptions()
                subscriptions_doc[constants.USER_ID] = ObjectId(self.get_current_user()[constants.MONGO_ID])
                subscriptions_doc[constants.USOS_ID] = self.get_current_user()[constants.USOS_ID]

                yield self.db_insert(constants.COLLECTION_SUBSCRIPTION, subscriptions_doc)
            self.success(subscriptions_doc)
        except Exception as ex:
            yield self.exc(ex)
