# coding=UTF-8

import logging
import traceback
from datetime import datetime, timedelta

import motor
from bson.objectid import ObjectId
from tornado.httpclient import HTTPError

from commons import constants
from commons.enumerators import ExceptionTypes
from commons.enumerators import JobStatus, JobType
from commons.errors import ApiError, AuthenticationError, CallerError
from commons.errors import DaoError


class DaoMixin(object):
    EXCEPTION_TYPE = ExceptionTypes.DAO.value

    def do_refresh(self):
        return False

    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)
        return self._db[self.config.MONGODB_NAME]

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

        if self.get_current_user():
            exc_doc[constants.USER_ID] = self.getUserId()

        exc_doc['traceback'] = traceback.format_exc()
        stack = traceback.extract_stack()
        filename, codeline, function_name, text = stack[-2]

        exc_doc['codeline'] = codeline
        exc_doc['function_name'] = function_name
        exc_doc['exception_type'] = self.EXCEPTION_TYPE if hasattr(self,
                                                                   'EXCEPTION_TYPE') else ExceptionTypes.UNKNOWN.value
        exc_doc[constants.CREATED_TIME] = datetime.now()

        if not isinstance(exception, AuthenticationError):
            await self.db_insert(constants.COLLECTION_EXCEPTIONS, exc_doc, update=False)

        if finish:
            if isinstance(exception, ApiError):
                self.error(message=str(exception))
            elif isinstance(exception, AuthenticationError):
                self.error(message=str(exception), code=401)
            elif isinstance(exception, CallerError) or isinstance(exception, HTTPError):
                self.usos()
            else:
                self.fail(message='Wystąpił błąd techniczny, pracujemy nad rozwiązaniem.')

    async def _manipulate_usoses(self, usoses_doc):
        result = []
        for usos in usoses_doc:
            usos[constants.USOS_LOGO] = self.config.DEPLOY_WEB + usos[constants.USOS_LOGO]

            if self.config.ENCRYPT_USOSES_KEYS:
                usos = dict(self.aes.decrypt_usos(usos))

            result.append(usos)
        return result

    async def get_usos_instances(self):
        usoses_doc = await self.db_usoses()
        return usoses_doc

    async def db_usoses(self, enabled=True):
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': enabled})
        usoses_doc = await cursor.to_list(None)
        return await self._manipulate_usoses(usoses_doc)

    async def db_all_usoses(self, limit_fields=True):
        if limit_fields:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({},
                                                                      {constants.MONGO_ID: 0, "contact": 1,
                                                                       "enabled": 1, "logo": 1, "name": 1, "phone": 1,
                                                                       "url": 1, "usos_id": 1, "comment": 1})
        else:
            cursor = self.db[constants.COLLECTION_USOSINSTANCES].find()
        usoses_doc = await cursor.to_list(None)
        return await self._manipulate_usoses(usoses_doc)

    async def db_users_info_by_user_id(self, user_id, usos):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return await self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: user_id,
                                                                        constants.USOS_ID: usos})

    async def db_get_user(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})

    async def db_get_usos(self, usos_id):
        return await self.db[constants.COLLECTION_USOSINSTANCES].find_one({
            'enabled': True, constants.USOS_ID: usos_id
        })

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
        pipeline_remove = pipeline.copy()

        pipeline_remove[constants.CREATED_TIME] = {
            '$lt': datetime.now() - timedelta(seconds=constants.SECONDS_REMOVE_ON_REFRESH)}

        result = await self.db[collection].remove(pipeline_remove)
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
        return await self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: programme_id,
                                                                        constants.USOS_ID: usos_id})

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
        return await self.db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id,
                                                                   constants.USOS_ID: usos_id})

    async def db_faculty(self, fac_id, usos_id):
        return await self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: fac_id,
                                                                       constants.USOS_ID: usos_id})

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
        return await self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: user_id,
                                                                        constants.USOS_ID: usos_id})

    async def db_get_archive_user(self, user_id):
        return await self.db[constants.COLLECTION_USERS_ARCHIVE].find_one(
            {constants.USER_ID: user_id, constants.USOS_PAIRED: True})

    async def db_archive_user(self, user_id):
        user_doc = await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})

        if not user_doc:
            logging.warning('cannot archive user which does not exists {0}'.format(user_id))
            return

        user_doc[constants.USER_ID] = user_doc.pop(constants.MONGO_ID)

        await self.db_insert(constants.COLLECTION_USERS_ARCHIVE, user_doc)

        await self.db_remove(constants.COLLECTION_USERS, {constants.MONGO_ID: user_id})
        if user_doc[constants.USOS_PAIRED]:
            await self.db_insert(constants.COLLECTION_JOBS_QUEUE,
                                 {constants.USER_ID: user_id,
                                  constants.CREATED_TIME: datetime.now(),
                                  constants.UPDATE_TIME: None,
                                  constants.JOB_MESSAGE: None,
                                  constants.JOB_STATUS: JobStatus.PENDING.value,
                                  constants.JOB_TYPE: JobType.ARCHIVE_USER.value})

    async def db_find_user(self):
        return await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: self.getUserId()})

    async def db_find_user_by_usos_id(self, user_id, usos_id):
        '''
        :param user_id:
        :param usos_id:
        :return: document from  COLLECTION_USERS
        '''

        if not isinstance(user_id, str):
            user_id = str(user_id)

        user_doc = await self.db[constants.COLLECTION_USERS].find_one({
            constants.USOS_USER_ID: user_id,
            constants.USOS_ID: usos_id
        })

        if not user_doc:
            raise DaoError('Nie znaleziono użytkownika na podstawie użytkownika usos: {0} dla usos: {1}'.format(
                user_id, usos_id))

        return user_doc

    async def db_cookie_user_id(self, user_id):
        user_doc = await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})

        if constants.GOOGLE in user_doc:
            user_doc[constants.PICTURE] = user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE]
            del (user_doc[constants.GOOGLE])

        if constants.FACEBOOK in user_doc:
            user_doc[constants.PICTURE] = user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE]
            del (user_doc[constants.FACEBOOK])

        return user_doc

    async def db_find_user_email(self, email):
        if not isinstance(email, str):
            email = str(email)

        return await self.db[constants.COLLECTION_USERS].find_one({constants.USER_EMAIL: email.lower()})

    async def db_update(self, collection, _id, document):
        updated = await self.db[collection].update({constants.MONGO_ID: _id}, document)
        logging.debug('collection: {0} updated: {1}'.format(collection, updated))
        return updated

    async def db_update_user(self, _id, document):
        return await self.db_update(constants.COLLECTION_USERS, _id, document)

    async def db_insert_user(self, document):
        user_doc = await self.db_insert(constants.COLLECTION_USERS, document)
        return user_doc

    async def db_insert_token(self, token):
        await self.db[constants.COLLECTION_TOKENS].remove({constants.USER_EMAIL: token[constants.USER_EMAIL]})
        return await self.db_insert(constants.COLLECTION_TOKENS, token)

    async def db_remove_token(self, email):
        result = await self.db[constants.COLLECTION_TOKENS].remove({constants.USER_EMAIL: email})
        logging.debug(
            'removed from collection {0} token for email {1} resulted in {2}'.format(constants.USER_EMAIL, email,
                                                                                     result))

    async def db_find_token(self, email):
        '''
        finds token by email and updates creation time
        :param email:
        :return: token_doc
        '''

        token_doc = await self.db[constants.COLLECTION_TOKENS].find_one({constants.USER_EMAIL: email})
        if token_doc:
            token_doc[constants.CREATED_TIME] = datetime.now()
            await self.db_update(constants.COLLECTION_TOKENS, token_doc[constants.MONGO_ID], token_doc)
        return token_doc

    async def db_subscriptions(self, pipeline):
        cursor = self.db[constants.COLLECTION_SUBSCRIPTIONS].find(pipeline)
        subscriptions = await cursor.to_list(None)
        return subscriptions

    async def db_messages(self, pipeline):
        cursor = self.db[constants.COLLECTION_MESSAGES].find(pipeline, {constants.MONGO_ID: 0,
                                                                        "typ": 1,
                                                                        "from": 1,
                                                                        constants.CREATED_TIME: 1,
                                                                        constants.JOB_MESSAGE: 1}
                                                             )
        return await cursor.to_list(None)

    async def db_user_usos_id(self):
        user_doc = await self.db_find_user()
        if user_doc and constants.USOS_USER_ID in user_doc:
            return user_doc[constants.USOS_USER_ID]
        return

    async def db_save_message(self, message, user_id=None, message_type=None, from_whom=None):
        if not message_type:
            message_type = 'email'

        if not from_whom:
            from_whom = self.config.PROJECT_TITLE

        if not user_id:
            user_id = self.getUserId()

        return await self.db[constants.COLLECTION_MESSAGES].insert({
            constants.USER_ID: user_id,
            constants.CREATED_TIME: datetime.now(),
            constants.FIELD_MESSAGE_FROM: from_whom,
            constants.FIELD_MESSAGE_TYPE: message_type,
            constants.FIELD_MESSAGE_TEXT: message,
        })

    async def db_settings(self, user_id):
        settings = await self.db[constants.COLLECTION_SETTINGS].find_one({constants.USER_ID: user_id})
        if settings:
            del settings[constants.USER_ID]
            del settings[constants.MONGO_ID]
            return settings

        return dict()

    async def db_settings_update(self, user_id, key, value):
        settings = await self.db[constants.COLLECTION_SETTINGS].find_one({constants.USER_ID: user_id})
        if not settings:
            return await self.db[constants.COLLECTION_SETTINGS].insert({
                constants.USER_ID: user_id,
                key: value
            })
        
        settings[key] = value
        return await self.db[constants.COLLECTION_SETTINGS].update_one({constants.USER_ID: user_id},
                                                                       {'$set': {key: value}})
