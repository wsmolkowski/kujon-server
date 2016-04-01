# coding=UTF-8

import logging

import motor
from bson.objectid import ObjectId
from tornado import gen
from tornado.ioloop import IOLoop

from commons import constants, settings
from crawler import job_factory


class DatabaseMixin(object):
    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    @gen.coroutine
    def remove_user(self, user_id):
        result = yield self.db[constants.COLLECTION_USERS].remove({constants.MONGO_ID: user_id})
        logging.debug('removed data from collection {0} for user {1} with result {2}'.format(
            constants.COLLECTION_USERS, user_id, result))

        result = self.db[constants.COLLECTION_JOBS_QUEUE].insert(job_factory.remove_user_job(user_id))
        logging.debug('created job for removing user data {0}'.format(result))

    @gen.coroutine
    def remove_user_data(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        logging.debug('removing user data for user_id {0}'.format(user_id))

        collections = yield self.db.collection_names()
        for collection in collections:
            exists = yield self.db[collection].find_one({constants.USER_ID: {'$exists': True, '$ne': False}})
            if exists:
                result = yield self.db[collection].remove({constants.USER_ID: user_id})
                logging.debug('removed data from collection {0} for user {1} with result {2}'.format(
                    collection, user_id, result))

        logging.debug('removed user data for user_id {0}'.format(user_id))

