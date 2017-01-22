# coding=UTF-8

import logging
from datetime import datetime

from bson.objectid import ObjectId

from commons.AESCipher import AESCipher
from commons.OneSignal import OneSignal
from commons.constants import fields, collections
from commons.context import Context
from commons.enumerators import ExceptionTypes
from commons.mixins.ApiTermMixin import ApiTermMixin
from commons.mixins.CrsTestsMixin import CrsTestsMixin


class UsosCrawler(CrsTestsMixin, ApiTermMixin):
    EXCEPTION_TYPE = ExceptionTypes.CRAWLER.value

    def __init__(self, config):
        self.config = config
        self._aes = AESCipher(self.config.AES_SECRET)
        self._osm = OneSignal(self.config)
        self._context = Context(self.config)  # initial empty context for cases when user is not set up

    @property
    def aes(self):
        return self._aes

    async def _buildContext(self, user_id, refresh=False):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        user_doc = await self.db[collections.USERS].find_one({fields.MONGO_ID: user_id})
        if not user_doc:
            user_doc = await self.db_get_archive_user(user_id)

        usos_doc = await self.db_get_usos(user_doc[fields.USOS_ID])
        self._context = Context(self.config, user_doc=user_doc, usos_doc=usos_doc, refresh=refresh)
        self._context.settings = await self.db_settings(self.getUserId())

    def doRefresh(self):
        return self._context.refresh

    def get_current_user(self):
        return self._context.user_doc

    def get_current_usos(self):
        return self._context.usos_doc

    def getUserId(self, return_object_id=True):
        if self.get_current_user():
            if return_object_id:
                return self.get_current_user()[fields.MONGO_ID]
            return str(self.get_current_user()[fields.MONGO_ID])
        return

    def getEncryptedUserId(self):
        return self.aes.encrypt(self.getUserId(return_object_id=False)).decode()

    def getUsosId(self):
        if self.get_current_usos():
            return self.get_current_user()[fields.USOS_ID]
        return

    def get_auth_http_client(self):
        return self._context.http_client

    async def usosCall(self, path, arguments=None):
        return await self._context.usosCaller.call(path, arguments)

    async def asyncCall(self, path, arguments=None, base_url=None, lang=True):
        return await self._context.asyncCaller.call_async(path, arguments, base_url, lang)

    async def initial_user_crawl(self, user_id, refresh=False):
        try:
            await self._buildContext(user_id)

            if refresh:
                skip_collections = [collections.USERS, collections.JOBS_QUEUE,
                                    collections.JOBS_LOG, collections.MESSAGES,
                                    collections.SEARCH, collections.TOKENS,
                                    collections.EXCEPTIONS, collections.SUBSCRIPTIONS,
                                    collections.REMOTE_IP_HISTORY]

                await self.remove_user_data(skip_collections)

            user_doc = await self.api_user_usos_info()

            await self._buildContext(user_id)

            await self.api_thesis(user_info=user_doc)
            await self.api_terms()
            await self.api_programmes(user_info=user_doc)
            await self.api_faculties(user_info=user_doc)

        except Exception as ex:
            await self.exc(ex, finish=False)

    async def unsubscribe(self, user_id=None):
        if user_id:
            await self._buildContext(user_id)

        try:
            current_subscriptions = await self.usosCall(path='services/events/subscriptions')
        except Exception as ex:
            logging.exception(ex)
            current_subscriptions = None

        if current_subscriptions:
            try:
                await self.usosCall(path='services/events/unsubscribe')
                await self.db_remove(collections.SUBSCRIPTIONS, {fields.USER_ID: self.getUserId()})
            except Exception as ex:
                logging.warning(ex)

    async def subscribe(self, user_id):

        await self._buildContext(user_id)

        await self.unsubscribe()

        callback_url = '{0}/{1}/{2}'.format(self.config.DEPLOY_EVENT, self.getUsosId(), user_id)

        for event_type in ['crstests/user_grade', 'grades/grade', 'crstests/user_point']:
            try:
                subscribe_doc = await self.usosCall(path='services/events/subscribe_event',
                                                    arguments={
                                                        'event_type': event_type,
                                                        'callback_url': callback_url,
                                                        'verify_token': self.getEncryptedUserId()
                                                    })
                subscribe_doc['event_type'] = event_type
                subscribe_doc[fields.USER_ID] = self.getUserId()

                await self.db_insert(collections.SUBSCRIPTIONS, subscribe_doc)
            except Exception as ex:
                await self.exc(ex, finish=False)

    async def notifier_status(self):
        # unused
        try:
            timestamp = datetime.now()

            usoses = await self.db_usoses()
            for usos_doc in usoses:
                try:
                    data = await self.asyncCall(path='services/events/notifier_status',
                                                base_url=usos_doc[fields.USOS_URL])

                    data[fields.CREATED_TIME] = timestamp
                    data[fields.USOS_ID] = usos_doc[fields.USOS_ID]

                    await self.db_insert(collections.NOTIFIER_STATUS, data)
                except Exception as ex:
                    await self.exc(ex, finish=False)

        except Exception as ex:
            self.exc(ex, finish=False)
