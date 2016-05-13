# coding=UTF-8

import logging
import traceback
from datetime import datetime

from tornado import gen
from tornado.web import RequestHandler

from commons import constants, settings
from commons.errors import ApiError, AuthenticationError
from crawler import email_factory

TOKEN_EXPIRATION_TIMEOUT = 3600


class DatabaseHandler(RequestHandler):
    EXCEPTION_TYPE = 'api'

    @property
    def db(self):
        return self.application.db

    @gen.coroutine
    def archive_user(self, user_id):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})

        if not user_doc:
            logging.warn('cannot archive user which does not exists {0}'.format(user_id))
            raise gen.Return()

        user_doc[constants.USER_ID] = user_doc.pop(constants.MONGO_ID)

        yield self.insert(constants.COLLECTION_USERS_ARCHIVE, user_doc)

        result = yield self.db[constants.COLLECTION_USERS].remove({constants.MONGO_ID: user_id})

        logging.debug('removed data from collection {0} for user {1} with result {2}'.format(
            constants.COLLECTION_USERS, user_id, result))

        yield self.insert(constants.COLLECTION_JOBS_QUEUE,
                          {constants.USER_ID: user_id,
                           constants.CREATED_TIME: datetime.now(),
                           constants.UPDATE_TIME: None,
                           constants.JOB_MESSAGE: None,
                           constants.JOB_STATUS: constants.JOB_PENDING,
                           constants.JOB_TYPE: 'unsubscribe_usos'})

        yield self.insert(constants.COLLECTION_JOBS_QUEUE,
                          {constants.USER_ID: user_id,
                           constants.CREATED_TIME: datetime.now(),
                           constants.UPDATE_TIME: None,
                           constants.JOB_MESSAGE: None,
                           constants.JOB_STATUS: constants.JOB_PENDING,
                           constants.JOB_TYPE: 'archive_user'})

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
            '\nCześć,\n'
            '\nRejestracja Twojego konta do współpracy z uczelnią {0} zakończona pomyślnie.'
            '\nW razie pytań, bądź pomysłów na zmianę - napisz do nas, bo dzięki Tobie Kujon może być lepszy..\n'
            '\nPozdrawiamy,'
            '\nZespół Kujon.mobi'
            '\nemail: {1}\n'.format(usos_doc['name'], settings.SMTP_EMAIL)
        )

        yield self.insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

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

        yield self.insert(constants.COLLECTION_EMAIL_QUEUE, email_job)

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
    def find_user_info(self, id):
        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: id})
        raise gen.Return(user_info_doc)

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
            raise gen.Return(user_doc)
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
    def exc(self, exception):
        if isinstance(exception, ApiError):
            exc_doc = exception.data()
        else:
            exc_doc = {
                'exception': str(exception.message)
            }

        if hasattr(self, 'user_doc'):
            exc_doc[constants.USOS_ID] = self.user_doc[constants.USOS_ID]
            exc_doc[constants.USER_ID] = self.user_doc[constants.MONGO_ID]

        exc_doc[constants.TRACEBACK] = traceback.format_exc()
        exc_doc[constants.EXCEPTION_TYPE] = self.EXCEPTION_TYPE
        exc_doc[constants.CREATED_TIME] = datetime.now()

        ex_id = yield self.insert(constants.COLLECTION_EXCEPTIONS, exc_doc)

        logging.exception('handled exception {0} and saved in db with {1}'.format(exc_doc, ex_id))

        if isinstance(exception, ApiError):
            self.error(message=exception.message())
        elif isinstance(exception, AuthenticationError):
            self.error(message=exception.message)
        else:
            self.fail(message='Wystąpił błąd techniczny. Pracujemy nad rozwiązaniem.')

        raise gen.Return()

    @gen.coroutine
    def get_classtypes(self, usos_id):

        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find({constants.USOS_ID: usos_id})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        raise gen.Return(classtypes)

    @gen.coroutine
    def get_terms_with_order_keys(self, usos_id, terms_list):

        terms_by_order = dict()
        for term in terms_list:
            term_coursor = self.db[constants.COLLECTION_TERMS].find(
                {constants.USOS_ID: usos_id,
                 constants.TERM_ID: term},
                (constants.TERM_ID, constants.TERMS_ORDER_KEY))
            while (yield term_coursor.fetch_next):
                term_doc = term_coursor.next_object()
            terms_by_order[term_doc[constants.TERMS_ORDER_KEY]] = term_doc[constants.TERM_ID]

        raise gen.Return(terms_by_order)

    @gen.coroutine
    def get_classtypes(self):

        classtypes = dict()
        cursor = self.db[constants.COLLECTION_COURSES_CLASSTYPES].find(
            {constants.USOS_ID: self.user_doc[constants.USOS_ID]})
        while (yield cursor.fetch_next):
            ct = cursor.next_object()
            classtypes[ct['id']] = ct['name']['pl']

        raise gen.Return(classtypes)
