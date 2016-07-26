# coding=UTF-8

import logging
import traceback
from datetime import datetime, timedelta

import motor
from bson.objectid import ObjectId
from tornado import gen

from commons import constants, settings
from commons.errors import ApiError, AuthenticationError, UsosClientError
from commons.errors import DaoError


class DaoMixin(object):
    EXCEPTION_TYPE = 'dao'

    def do_refresh(self):
        return False

    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    @gen.coroutine
    def exc(self, exception, finish=True):
        logging.exception(exception)

        if isinstance(exception, ApiError):
            exc_doc = exception.data()
        else:
            exc_doc = {
                'exception': str(exception)
            }

        if hasattr(self, 'get_current_user') and self.get_current_user():
            user_id = self.get_current_user()[constants.MONGO_ID]
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
            exc_doc[constants.USER_ID] = user_id

        exc_doc[constants.TRACEBACK] = traceback.format_exc()
        exc_doc[constants.EXCEPTION_TYPE] = self.EXCEPTION_TYPE
        exc_doc[constants.CREATED_TIME] = datetime.now()

        yield self.db_insert(constants.COLLECTION_EXCEPTIONS, exc_doc)

        if finish:
            if isinstance(exception, ApiError):
                self.error(message=exception.message())
            elif isinstance(exception, AuthenticationError):
                self.error(message=exception)
            elif isinstance(exception, UsosClientError):
                self.error(message='Wystąpił błąd USOS.')
            else:
                self.fail(message='Wystąpił błąd techniczny, pracujemy nad rozwiązaniem.')

        raise gen.Return()

    @gen.coroutine
    def get_usos_instances(self):
        result = []
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
        usoses_doc = yield cursor.to_list(None)
        for usos in usoses_doc:
            usos[constants.USOS_LOGO] = settings.DEPLOY_WEB + usos[constants.USOS_LOGO]

            if settings.ENCRYPT_USOSES_KEYS:
                usos = dict(self.aes.decrypt_usos(usos))

            result.append(usos)

        raise gen.Return(result)

    @gen.coroutine
    def db_users_info_by_user_id(self, user_id, usos):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: user_id,
                                                                                 constants.USOS_ID: usos})

        raise gen.Return(user_info_doc)

    @gen.coroutine
    def db_get_user(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})
        raise gen.Return(user_doc)

    @gen.coroutine
    def db_get_usos(self, usos_id):
        usos_doc = yield self.db[constants.COLLECTION_USOSINSTANCES].find_one({
            'enabled': True, constants.USOS_ID: usos_id
        })
        raise gen.Return(usos_doc)

    @gen.coroutine
    def db_insert(self, collection, document):
        create_time = datetime.now()
        if hasattr(self, '_context') and hasattr(self._context, 'usos_doc'):
            document[constants.USOS_ID] = self._context.usos_doc[constants.USOS_ID]
        document[constants.CREATED_TIME] = create_time
        document[constants.UPDATE_TIME] = create_time

        doc = yield self.db[collection].insert(document)
        logging.debug("document {0} inserted into collection: {1}".format(doc, collection))
        raise gen.Return(doc)

    @gen.coroutine
    def db_remove(self, collection, pipeline):
        result = yield self.db[collection].remove(pipeline)
        logging.debug("removed docs from collection {0} with {1}".format(collection, result))
        raise gen.Return(result)

    @gen.coroutine
    def db_users_info_programmes(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        programmes = []
        data = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: user_id})
        if data:
            programmes = data['student_programmes']
        raise gen.Return(programmes)

    @gen.coroutine
    def db_programme(self, programme_id, usos_id):
        programme_doc = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: programme_id,
                                                                                 constants.USOS_ID: usos_id})
        raise gen.Return(programme_doc)

    @gen.coroutine
    def db_courses_editions(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        result = list()
        data = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: user_id})
        if not data:
            raise gen.Return(result)

        for term_data in data['course_editions'].values():
            for term in term_data:
                tc = {constants.TERM_ID: term[constants.TERM_ID], constants.COURSE_ID: term[constants.COURSE_ID]}
                if tc not in result:
                    result.append(tc)

        raise gen.Return(result)

    @gen.coroutine
    def db_courses(self, usos_id):
        cursor = self.db[constants.COLLECTION_COURSES].find({constants.USOS_ID: usos_id})
        courses = yield cursor.to_list(None)
        raise gen.Return(courses)

    @gen.coroutine
    def db_terms(self, user_id):
        terms = list()
        data = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: user_id})
        for term in data['course_editions'].keys():
            if term not in terms:
                terms.append(term)
        raise gen.Return(terms)

    @gen.coroutine
    def db_term(self, term_id, usos_id):
        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id,
                                                                       constants.USOS_ID: usos_id})
        raise gen.Return(term_doc)

    @gen.coroutine
    def db_faculty(self, fac_id, usos_id):
        faculty_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: fac_id,
                                                                              constants.USOS_ID: usos_id})

        raise gen.Return(faculty_doc)

    @gen.coroutine
    def db_users(self):
        cursor = self.db[constants.COLLECTION_USERS].find({constants.USOS_PAIRED: True},
                                                          (constants.MONGO_ID,
                                                           constants.USOS_ID,
                                                           constants.ACCESS_TOKEN_KEY,
                                                           constants.ACCESS_TOKEN_SECRET))

        users = yield cursor.to_list(None)
        raise gen.Return(users)

    @gen.coroutine
    def db_courses_conducted(self, user_id):
        course_editions_conducted = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: user_id}, ('course_editions_conducted',))

        if course_editions_conducted and 'course_editions_conducted' in course_editions_conducted:
            raise gen.Return(course_editions_conducted['course_editions_conducted'])

        raise gen.Return([])

    @gen.coroutine
    def db_users_info(self, user_id, usos_id):
        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: user_id,
                                                                                 constants.USOS_ID: usos_id})
        raise gen.Return(user_info_doc)

    @gen.coroutine
    def db_get_archive_user(self, user_id):
        user_archive_doc = yield self.db[constants.COLLECTION_USERS_ARCHIVE].find_one(
            {constants.USER_ID: user_id, constants.USOS_PAIRED: True})

        raise gen.Return(user_archive_doc)

    @gen.coroutine
    def db_usoses(self, enabled=True):
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': enabled})
        usoses = yield cursor.to_list(None)
        raise gen.Return(usoses)

    @gen.coroutine
    def db_archive_user(self, user_id):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})

        if not user_doc:
            logging.warning('cannot archive user which does not exists {0}'.format(user_id))
            raise gen.Return()

        user_doc[constants.USER_ID] = user_doc.pop(constants.MONGO_ID)

        yield self.db_insert(constants.COLLECTION_USERS_ARCHIVE, user_doc)

        yield self.db_remove(constants.COLLECTION_USERS, {constants.MONGO_ID: user_id})
        if user_doc[constants.USOS_PAIRED]:
            # yield self.db_insert(constants.COLLECTION_JOBS_QUEUE,
            #                      {constants.USER_ID: user_id,
            #                       constants.CREATED_TIME: datetime.now(),
            #                       constants.UPDATE_TIME: None,
            #                       constants.JOB_MESSAGE: None,
            #                       constants.JOB_STATUS: constants.JOB_PENDING,
            #                       constants.JOB_TYPE: 'unsubscribe_usos'})

            yield self.db_insert(constants.COLLECTION_JOBS_QUEUE,
                                 {constants.USER_ID: user_id,
                                  constants.CREATED_TIME: datetime.now(),
                                  constants.UPDATE_TIME: None,
                                  constants.JOB_MESSAGE: None,
                                  constants.JOB_STATUS: constants.JOB_PENDING,
                                  constants.JOB_TYPE: 'archive_user'})

    @gen.coroutine
    def db_find_user(self):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: self.get_current_user()[constants.MONGO_ID]})

        raise gen.Return(user_doc)

    @gen.coroutine
    def db_find_user_id(self, user_id):
        if not isinstance(user_id, str):
            user_id = str(user_id)

        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one({
            constants.ID: user_id
        })

        if constants.USER_ID in user_info_doc:
            user_doc = yield self.db[constants.COLLECTION_USERS].find_one({
                constants.MONGO_ID: ObjectId(user_info_doc[constants.USER_ID])
            })

            raise gen.Return(user_doc)

        raise DaoError('Nie znaleziono użytkownika aplikacyjnego na podstawie użytkownika usos: {0}'.format(user_id))

    @gen.coroutine
    def db_cookie_user_id(self, user_id):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id},
                                                                      constants.COOKIE_FIELDS)

        if constants.GOOGLE in user_doc:
            user_doc[constants.PICTURE] = user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE]
            del (user_doc[constants.GOOGLE])

        if constants.FACEBOOK in user_doc:
            user_doc[constants.PICTURE] = user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE]
            del (user_doc[constants.FACEBOOK])

        raise gen.Return(user_doc)

    @gen.coroutine
    def db_find_user_email(self, email):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email})
        raise gen.Return(user_doc)

    @gen.coroutine
    def db_update(self, collection, _id, document):
        updated = yield self.db[collection].update({constants.MONGO_ID: _id}, document)
        logging.debug('collection: {0} updated: {1}'.format(collection, updated))
        raise gen.Return(updated)

    @gen.coroutine
    def db_current_user(self, email):
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email},
                                                                      (constants.ID, constants.ACCESS_TOKEN_KEY,
                                                                       constants.ACCESS_TOKEN_SECRET, constants.USOS_ID,
                                                                       constants.USOS_PAIRED, constants.USER_EMAIL)
                                                                      )
        raise gen.Return(user_doc)

    @gen.coroutine
    def db_update_user(self, _id, document):
        update_doc = yield self.db_update(constants.COLLECTION_USERS, _id, document)
        raise gen.Return(update_doc)

    @gen.coroutine
    def db_insert_user(self, document):
        user_doc = yield self.db_insert(constants.COLLECTION_USERS, document)
        raise gen.Return(user_doc)

    @gen.coroutine
    def db_insert_token(self, token):
        yield self.db_remove(constants.COLLECTION_TOKENS, token)
        if constants.FIELD_TOKEN_EXPIRATION not in token:
            token[constants.FIELD_TOKEN_EXPIRATION] = datetime.now() + timedelta(
                seconds=constants.TOKEN_EXPIRATION_TIMEOUT)

        token_doc = yield self.db_insert(constants.COLLECTION_TOKENS, token)
        raise gen.Return(token_doc)

    @gen.coroutine
    def db_find_token(self, email):
        token_doc = yield self.db[constants.COLLECTION_TOKENS].find_one({constants.USER_EMAIL: email})
        raise gen.Return(token_doc)

    @gen.coroutine
    def db_subscriptions(self, pipeline):
        cursor = self.db[constants.COLLECTION_SUBSCRIPTIONS].find(pipeline)
        subscriptions = yield cursor.to_list(None)
        raise gen.Return(subscriptions)
