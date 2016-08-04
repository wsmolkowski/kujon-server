# coding=UTF-8

import logging
import traceback
from datetime import datetime, timedelta

import motor
from bson.objectid import ObjectId
from tornado.httpclient import HTTPError

from commons import constants
from commons.AESCipher import AESCipher
from commons.errors import ApiError, AuthenticationError, CallerError
from commons.errors import DaoError


class DaoMixin(object):
    EXCEPTION_TYPE = 'dao'

    @staticmethod
    def do_refresh():
        return False

    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)
        return self._db[self.config.MONGODB_NAME]

    _aes = None

    @property
    def aes(self):
        if not self._aes:
            self._aes = AESCipher(self.config.AES_SECRET)
        return self._aes

    async def exc(self, exception, finish=True):
        logging.exception(exception)

        exc_doc = {
            'exception': str(exception)
        }

        if isinstance(exception, HTTPError):
            exc_doc['code'] = exception.code
            exc_doc['message'] = exception.message
            if hasattr(exception, 'response') and hasattr(exception.response, 'body'):
                exc_doc['body'] = str(exception.response.body)
                exc_doc['effective_url'] = exception.response.effective_url

        if hasattr(self, 'get_current_user') and self.get_current_user():
            exc_doc[constants.USER_ID] = self.getUserId()

        exc_doc[constants.TRACEBACK] = traceback.format_exc()
        exc_doc[constants.EXCEPTION_TYPE] = self.EXCEPTION_TYPE
        exc_doc[constants.CREATED_TIME] = datetime.now()

        await self.db_insert(constants.COLLECTION_EXCEPTIONS, exc_doc, update=False)

        if finish:
            if isinstance(exception, ApiError) or isinstance(exception, AuthenticationError):
                self.error(message=str(exception))
            elif isinstance(exception, CallerError) or isinstance(exception, HTTPError):
                self.usos()
            else:
                self.fail(message='Wystąpił błąd techniczny, pracujemy nad rozwiązaniem.')

    async def get_usos_instances(self):
        result = []
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
        usoses_doc = await cursor.to_list(None)
        for usos in usoses_doc:
            usos[constants.USOS_LOGO] = self.config.DEPLOY_WEB + usos[constants.USOS_LOGO]

            if self.config.ENCRYPT_USOSES_KEYS:
                usos = dict(self.aes.decrypt_usos(usos))

            result.append(usos)

        return result

    async def db_users_info_by_user_id(self, user_id, usos):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_info_doc = await self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: user_id,
                                                                                 constants.USOS_ID: usos})

        return user_info_doc

    async def db_get_user(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_doc = await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})
        return user_doc

    async def db_get_usos(self, usos_id):
        usos_doc = await self.db[constants.COLLECTION_USOSINSTANCES].find_one({
            'enabled': True, constants.USOS_ID: usos_id
        })
        return usos_doc

    async def db_insert(self, collection, document, update=True):
        create_time = datetime.now()
        if self.getUsosId():
            document[constants.USOS_ID] = self.getUsosId()
        document[constants.CREATED_TIME] = create_time

        if update:
            document[constants.UPDATE_TIME] = create_time

        doc = await self.db[collection].insert(document)
        logging.debug("document {0} inserted into collection: {1}".format(doc, collection))
        return doc

    async def db_remove(self, collection, pipeline):
        result = await self.db[collection].remove(pipeline)
        logging.debug("removed docs from collection {0} with {1}".format(collection, result))
        return result

    async def db_users_info_programmes(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        programmes = []
        data = await self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: user_id})
        if data:
            programmes = data['student_programmes']
        return programmes

    async def db_programme(self, programme_id, usos_id):
        programme_doc = await self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: programme_id,
                                                                                 constants.USOS_ID: usos_id})
        return programme_doc

    async def db_courses_editions(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        result = list()
        data = await self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: user_id})
        if not data:
            return result

        for term_data in data['course_editions'].values():
            for term in term_data:
                tc = {constants.TERM_ID: term[constants.TERM_ID], constants.COURSE_ID: term[constants.COURSE_ID]}
                if tc not in result:
                    result.append(tc)

        return result

    async def db_courses(self, usos_id):
        cursor = self.db[constants.COLLECTION_COURSES].find({constants.USOS_ID: usos_id})
        courses = await cursor.to_list(None)
        return courses

    async def db_terms(self, user_id):
        terms = list()
        data = await self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: user_id})
        for term in data['course_editions'].keys():
            if term not in terms:
                terms.append(term)
        return terms

    async def db_term(self, term_id, usos_id):
        term_doc = await self.db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id,
                                                                       constants.USOS_ID: usos_id})
        return term_doc

    async def db_faculty(self, fac_id, usos_id):
        faculty_doc = await self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: fac_id,
                                                                              constants.USOS_ID: usos_id})

        return faculty_doc

    async def db_users(self):
        cursor = self.db[constants.COLLECTION_USERS].find({constants.USOS_PAIRED: True},
                                                          (constants.MONGO_ID,
                                                           constants.USOS_ID,
                                                           constants.ACCESS_TOKEN_KEY,
                                                           constants.ACCESS_TOKEN_SECRET))

        users = await cursor.to_list(None)
        return users

    async def db_courses_conducted(self, user_id):
        course_editions_conducted = await self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: user_id}, ('course_editions_conducted',))

        if course_editions_conducted and 'course_editions_conducted' in course_editions_conducted:
            return course_editions_conducted['course_editions_conducted']

        return list()

    async def db_users_info(self, user_id, usos_id):
        user_info_doc = await self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: user_id,
                                                                                 constants.USOS_ID: usos_id})
        return user_info_doc

    async def db_get_archive_user(self, user_id):
        user_archive_doc = await self.db[constants.COLLECTION_USERS_ARCHIVE].find_one(
            {constants.USER_ID: user_id, constants.USOS_PAIRED: True})

        return user_archive_doc

    async def db_usoses(self, enabled=True):
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': enabled})
        usoses = await cursor.to_list(None)
        return usoses

    async def db_archive_user(self, user_id):
        user_doc = await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})

        if not user_doc:
            logging.warning('cannot archive user which does not exists {0}'.format(user_id))
            return None

        user_doc[constants.USER_ID] = user_doc.pop(constants.MONGO_ID)

        await self.db_insert(constants.COLLECTION_USERS_ARCHIVE, user_doc)

        await self.db_remove(constants.COLLECTION_USERS, {constants.MONGO_ID: user_id})
        if user_doc[constants.USOS_PAIRED]:
            await self.db_insert(constants.COLLECTION_JOBS_QUEUE,
                                 {constants.USER_ID: user_id,
                                  constants.CREATED_TIME: datetime.now(),
                                  constants.UPDATE_TIME: None,
                                  constants.JOB_MESSAGE: None,
                                  constants.JOB_STATUS: constants.JOB_PENDING,
                                  constants.JOB_TYPE: 'archive_user'})

    async def db_find_user(self):
        user_doc = await self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: self.getUserId()})

        return user_doc

    async def db_find_users_id(self, user_id, usos_id):
        '''
        :param user_id:
        :param usos_id:
        :return: list of documents from  COLLECTION_USERS
        '''

        if not isinstance(user_id, str):
            user_id = str(user_id)

        cursor = await self.db[constants.COLLECTION_USERS].find_one({
            constants.USOS_USER_ID: user_id,
            constants.USOS_ID: usos_id
        })

        users_info_doc = await cursor.to_list(None)

        if not users_info_doc:
            raise DaoError('Nie znaleziono użytkownika na podstawie użytkownika usos: {0} dla usos: {1}'.format(
                user_id, usos_id))

        return users_info_doc

    async def db_cookie_user_id(self, user_id):
        user_doc = await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id},
                                                                      constants.COOKIE_FIELDS)

        if constants.GOOGLE in user_doc:
            user_doc[constants.PICTURE] = user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE]
            del (user_doc[constants.GOOGLE])

        if constants.FACEBOOK in user_doc:
            user_doc[constants.PICTURE] = user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE]
            del (user_doc[constants.FACEBOOK])

        return user_doc

    async def db_find_user_email(self, email):
        user_doc = await self.db[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email})
        return user_doc

    async def db_update(self, collection, _id, document):
        updated = await self.db[collection].update({constants.MONGO_ID: _id}, document)
        logging.debug('collection: {0} updated: {1}'.format(collection, updated))
        return updated

    async def db_update_user(self, _id, document):
        update_doc = await self.db_update(constants.COLLECTION_USERS, _id, document)
        return update_doc

    async def db_insert_user(self, document):
        user_doc = await self.db_insert(constants.COLLECTION_USERS, document)
        return user_doc

    async def db_insert_token(self, token):
        await self.db_remove(constants.COLLECTION_TOKENS, token)
        if constants.FIELD_TOKEN_EXPIRATION not in token:
            token[constants.FIELD_TOKEN_EXPIRATION] = datetime.now() + timedelta(
                seconds=constants.TOKEN_EXPIRATION_TIMEOUT)

        token_doc = await self.db_insert(constants.COLLECTION_TOKENS, token)
        return token_doc

    async def db_find_token(self, email):
        token_doc = await self.db[constants.COLLECTION_TOKENS].find_one({constants.USER_EMAIL: email})
        return token_doc

    async def db_subscriptions(self, pipeline):
        cursor = self.db[constants.COLLECTION_SUBSCRIPTIONS].find(pipeline)
        subscriptions = await cursor.to_list(None)
        return subscriptions

    async def db_messages(self, pipeline):
        cursor = self.db[constants.COLLECTION_MESSAGES].find(pipeline)
        messages = await cursor.to_list(None)
        return messages

    async def db_user_usos_id(self):
        user_doc = await self.db_find_user()
        if user_doc and constants.USOS_USER_ID in user_doc:
            return user_doc[constants.USOS_USER_ID]
        return None
