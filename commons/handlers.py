# coding=UTF-8

from datetime import datetime
import logging

from tornado import gen
from tornado.web import RequestHandler

from commons import constants


class DatabaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def dao(self):
        return self.application.dao

    @gen.coroutine
    def archive_user(self, user_id):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})
        user_doc[constants.USER_ID] = user_doc.pop(constants.MONGO_ID)

        user_archive = yield self.db[constants.COLLECTION_USERS_ARCHIVE].insert(user_doc)
        logging.debug('archived user data with id {0}'.format(user_archive))

        result = yield self.db[constants.COLLECTION_USERS].remove({constants.MONGO_ID: user_id})

        logging.debug('removed data from collection {0} for user {1} with result {2}'.format(
            constants.COLLECTION_USERS, user_id, result))

        result = yield self.db[constants.COLLECTION_JOBS_QUEUE].insert({
            constants.USER_ID: user_id,
            constants.CREATED_TIME: datetime.now(),
            constants.UPDATE_TIME: None,
            constants.JOB_MESSAGE: None,
            constants.JOB_STATUS: constants.JOB_PENDING,
            constants.JOB_TYPE: 'archive_user'
        })

        logging.debug('created job for removing user data {0}'.format(result))


    @gen.coroutine
    def log_exception(self, arguments, trace):
        yield self.db[constants.COLLECTION_EXCEPTIONS].insert({
            constants.CREATED_TIME: datetime.now(),
            'file': file,
            'arguments': arguments,
            'trace': trace
        })