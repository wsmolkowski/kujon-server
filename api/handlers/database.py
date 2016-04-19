# coding=UTF-8

import logging
from datetime import datetime

from tornado import gen
from tornado.web import RequestHandler

from commons import constants, settings
from crawler import email_factory

TOKEN_EXPIRATION_TIMEOUT = 3600


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

        if not user_doc:
            logging.debug('cannot archive user which does not exists {0}'.format(user_id))
            return

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

        yield self.email_archive_user(user_doc[constants.USER_EMAIL])

    @gen.coroutine
    def email_registration(self):

        user_doc = yield self.find_user()
        usos_doc = yield self.get_usos(constants.USOS_ID, user_doc[constants.USOS_ID])
        recipient = user_doc[constants.USER_EMAIL]

        email_job = email_factory.email_job(
            'Witamy w serwisie {0}.'.format(settings.PROJECT_TITLE),
            settings.SMTP_EMAIL,
            recipient if type(recipient) is list else [recipient],
            '\nCześć,'
            '\nRejestracja w USOS {0} zakończona pomyślnie.'
            '\nW razie pytań, bądź wątpliwości pozostajemy do Twojej dyspozycji.'
            '\nNapisz do nas {1}'
            '\nPozdrawiamy,'
            '\nZespół {2}\n'.format(usos_doc['name'], settings.SMTP_EMAIL, settings.PROJECT_TITLE)
        )

        yield self.db[constants.COLLECTION_EMAIL_QUEUE].insert(email_job)

    @gen.coroutine
    def email_archive_user(self, recipient):
        email_job = email_factory.email_job(
            'Pozdrowienia z serwisu {0}.'.format(settings.PROJECT_TITLE),
            settings.SMTP_EMAIL,
            recipient if type(recipient) is list else [recipient],
            '\nCześć,'
            '\nTwoje konto w serwisie zostało skasowane.'
            '\nW razie pytań, bądź wątpliwości pozostajemy do Twojej dyspozycji.'
            '\nNapisz do nas {0}'
            '\nPozdrawiamy,'
            '\nZespół {1}\n'.format(settings.SMTP_EMAIL, settings.PROJECT_TITLE)
        )

        yield self.db[constants.COLLECTION_EMAIL_QUEUE].insert(email_job)

    @gen.coroutine
    def find_user(self):
        current_user = yield self.get_current_user()
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: current_user[constants.MONGO_ID]})

        raise gen.Return(user_doc)

    @gen.coroutine
    def cookie_user_id(self, user_id):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id},
                                                                      self._COOKIE_FIELDS)
        raise gen.Return(user_doc)

    @gen.coroutine
    def cookie_user_email(self, email):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email},
                                                                      self._COOKIE_FIELDS)
        raise gen.Return(user_doc)

    @gen.coroutine
    def find_user_email(self, email):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email})
        raise gen.Return(user_doc)

    @gen.coroutine
    def update(self, collection, _id, document):
        updated = yield self.db[collection].update({constants.MONGO_ID: _id}, document)
        logging.debug('collection: {0} updated: {1}'.format(collection, updated))

    @gen.coroutine
    def current_user(self, email):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email},
                                                                      (constants.ID, constants.ACCESS_TOKEN_KEY,
                                                                       constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                                                                       constants.USOS_PAIRED)
                                                                      )
        raise gen.Return(user_doc)

    @gen.coroutine
    def update_user(self, _id, document):
        yield self.update(constants.COLLECTION_USERS, _id, document)

    @gen.coroutine
    def update_user_email(self, email, document):
        user_doc = yield self.find_user_email(email)
        yield self.update(constants.COLLECTION_USERS, user_doc[constants.MONGO_ID], document)

    @gen.coroutine
    def insert(self, collection, document):
        doc = yield self.db[collection].insert(document)
        logging.debug("document {0} inserted into collection: {1}".format(doc, collection))
        raise gen.Return(doc)

    @gen.coroutine
    def insert_user(self, document):
        user_doc = yield self.insert(constants.COLLECTION_USERS, document)
        raise gen.Return(user_doc)

    @gen.coroutine
    def user_exists(self, email, usos_id):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.USER_EMAIL: email, constants.USOS_ID: usos_id})
        if user_doc:
            raise gen.Return(True)
        raise gen.Return(False)

    @gen.coroutine
    def ttl_index(self, collection, field):
        indexes = yield self.db[collection].index_information()
        if field not in indexes:
            index = yield self.db[collection].create_index(field, expireAfterSeconds=TOKEN_EXPIRATION_TIMEOUT)
            logging.debug('created TTL index {0} on collection {1}, field {2}'.format(index, collection, field))
        raise gen.Return()

    @gen.coroutine
    def insert_token(self, token):
        result = yield self.db[constants.COLLECTION_TOKENS].remove({'email': token['email']})

        logging.debug('removed data from collection {0} for email {1} with result {2}'.format(
            constants.COLLECTION_TOKENS, token['email'], result))

        user_doc = yield self.insert(constants.COLLECTION_TOKENS, token)

        yield self.ttl_index(constants.COLLECTION_TOKENS, 'exp')
        raise gen.Return(user_doc)

    @gen.coroutine
    def find_token(self, email):
        token_doc = yield self.db[constants.COLLECTION_TOKENS].find_one({constants.USER_EMAIL: email})
        raise gen.Return(token_doc)

    @gen.coroutine
    def log_exception(self, arguments, trace):
        yield self.db[constants.COLLECTION_EXCEPTIONS].insert({
            constants.CREATED_TIME: datetime.now(),
            'file': file,
            'arguments': arguments,
            'trace': trace
        })