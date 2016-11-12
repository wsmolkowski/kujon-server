# coding=UTF-8

from base64 import b64decode

import tornado.web
from bson.objectid import ObjectId

from api.handlers.base import ApiHandler
from commons import constants, decorators
from commons import usosinstances
from commons.errors import ApiError

LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id',
    constants.PHOTO_URL, "{}.{}".format(constants.GOOGLE, constants.GOOGLE_NAME),
    "{}.{}".format(constants.GOOGLE, constants.GOOGLE_PICTURE),
    "{}.{}".format(constants.GOOGLE, constants.GOOGLE_EMAIL),
    "{}.{}".format(constants.FACEBOOK, constants.FACEBOOK_NAME),
    "{}.{}".format(constants.FACEBOOK, constants.FACEBOOK_PICTURE),
    "{}.{}".format(constants.FACEBOOK, constants.FACEBOOK_EMAIL))


class UsersInfoByIdApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self, user_info_id):

        try:
            user_info_doc = await self.api_user_info(user_info_id)
            self.success(user_info_doc, cache_age=constants.SECONDS_2MONTHS)
        except Exception as ex:
            await self.exc(ex)


class AbstractUserInfo(ApiHandler):
    async def _users_info(self):
        user_doc = await self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: self.getUserId()},
            LIMIT_FIELDS_USER)

        user_info = await self.api_user_usos_info()

        # upgrade only with values or insert new keys + values
        for k, v in list(user_info.items()):
            if k not in user_doc:
                user_doc[k] = user_info[k]

        # check if get photo needed
        if constants.PHOTO_URL in user_doc and user_doc[constants.PHOTO_URL]:
            user_doc[constants.PHOTO_URL] = user_info[constants.PHOTO_URL]
        else:
            if constants.GOOGLE in user_doc and constants.GOOGLE_PICTURE in user_doc[constants.GOOGLE]:
                user_doc[constants.PHOTO_URL] = user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE]
            if constants.FACEBOOK in user_doc and constants.FACEBOOK_PICTURE in user_doc[constants.FACEBOOK]:
                user_doc[constants.PHOTO_URL] = user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE]

        user_doc['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if
                                      usos[constants.USOS_ID] == user_doc[constants.USOS_ID]), None)

        user_doc['theses'] = await self.api_thesis(refresh=True, user_info=user_doc)

        del (user_doc[constants.UPDATE_TIME])
        del (user_doc[constants.MONGO_ID])

        return user_doc


class UsersInfoAllApi(AbstractUserInfo):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self):
        """
        for mobi use only
        :return: combined data from api: user_info, faculties, terms, programmes
        """
        try:
            user_doc = await self._users_info()

            faculties, terms, programmes = await self.api_faculties(user_doc),\
                                           await self.api_terms(), \
                                           await self.api_programmes(finish=False, user_info=user_doc)

            user_doc['faculties'] = faculties
            user_doc['terms'] = terms
            user_doc['programmes'] = programmes

            self.success(user_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)


class UsersInfoApi(AbstractUserInfo):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self):
        """
        :return:    join data from constants.COLLECTION_USERS and constants.COLLECTION_USERS_INFO and
                    school name from usosinstances.USOSINSTANCES
        """

        try:
            user_doc = await self._users_info()
            self.success(user_doc, cache_age=constants.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)


class UsersInfoPhotoApi(ApiHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    async def get(self, photo_id):

        try:
            if str(photo_id) == 'False' or str(photo_id) == 'True':
                raise ApiError('Nie podano odpowiedniego parametru photo_id')

            user_photo = await self.db[constants.COLLECTION_PHOTOS].find_one({constants.MONGO_ID: ObjectId(photo_id)})

            if user_photo and 'photo' in user_photo:
                self.set_header('Content-Type', 'image/jpeg')
                self.write(b64decode(user_photo['photo']))
            else:
                self.error('Nie znaleziono zdjęcia', code=404)
        except Exception as ex:
            await self.exc(ex)
