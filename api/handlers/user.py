# coding=UTF-8

from base64 import b64decode

from bson.objectid import ObjectId

from api.handlers.base.api import ApiHandler
from commons import decorators
from commons import usosinstances
from commons.constants import fields, collections, config
from commons.errors import ApiError

LIMIT_FIELDS_USER = (
    'email', 'user_created', 'user_type', 'family_name' 'given_name', 'update_time', 'picture', 'name', 'usos_id',
    fields.PHOTO_URL, "{}.{}".format(fields.GOOGLE, fields.GOOGLE_NAME),
    "{}.{}".format(fields.GOOGLE, fields.GOOGLE_PICTURE),
    "{}.{}".format(fields.GOOGLE, fields.GOOGLE_EMAIL),
    "{}.{}".format(fields.FACEBOOK, fields.FACEBOOK_NAME),
    "{}.{}".format(fields.FACEBOOK, fields.FACEBOOK_PICTURE),
    "{}.{}".format(fields.FACEBOOK, fields.FACEBOOK_EMAIL))


class UsersInfoByIdApi(ApiHandler):
    @decorators.authenticated
    async def get(self, user_info_id):

        try:
            user_info_doc = await self.api_user_info(user_info_id)
            self.success(user_info_doc, cache_age=config.SECONDS_2MONTHS)
        except Exception as ex:
            await self.exc(ex)


class AbstractUserInfo(ApiHandler):
    async def _users_info(self):
        user_doc = await self.db[collections.USERS].find_one(
            {fields.MONGO_ID: self.getUserId()},
            LIMIT_FIELDS_USER)

        user_info = await self.api_user_usos_info()

        # upgrade only with values or insert new keys + values
        for k, v in list(user_info.items()):
            if k not in user_doc:
                user_doc[k] = user_info[k]

        # check if get photo needed
        if fields.PHOTO_URL in user_doc and user_doc[fields.PHOTO_URL]:
            user_doc[fields.PHOTO_URL] = user_info[fields.PHOTO_URL]
        else:
            if fields.GOOGLE in user_doc and fields.GOOGLE_PICTURE in user_doc[fields.GOOGLE]:
                user_doc[fields.PHOTO_URL] = user_doc[fields.GOOGLE][fields.GOOGLE_PICTURE]
            if fields.FACEBOOK in user_doc and fields.FACEBOOK_PICTURE in user_doc[fields.FACEBOOK]:
                user_doc[fields.PHOTO_URL] = user_doc[fields.FACEBOOK][fields.FACEBOOK_PICTURE]

        user_doc['usos_name'] = next((usos['name'] for usos in usosinstances.USOSINSTANCES if
                                      usos[fields.USOS_ID] == user_doc[fields.USOS_ID]), None)

        user_doc['theses'] = await self.api_thesis(refresh=True, user_info=user_doc)

        del (user_doc[fields.UPDATE_TIME])
        del (user_doc[fields.MONGO_ID])

        return user_doc


class UsersInfoAllApi(AbstractUserInfo):
    @decorators.authenticated
    async def get(self):
        """
        for mobi use only
        :return: combined data from api: user_info, faculties, terms, programmes
        """
        try:
            user_doc = await self._users_info()

            faculties, terms, programmes = await self.api_faculties(user_doc), \
                                           await self.api_terms(), \
                                           await self.api_programmes(finish=False, user_info=user_doc)

            user_doc['faculties'] = faculties
            user_doc['terms'] = terms
            user_doc['programmes'] = programmes

            user_doc['avr_grades'] = await self.api_average_grades()

            self.success(user_doc, cache_age=config.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)


class UsersInfoApi(AbstractUserInfo):
    @decorators.authenticated
    async def get(self):
        """
        :return:    join data from collections.USERS and collections.USERS_INFO and
                    school name from usosinstances.USOSINSTANCES
        """

        try:
            user_doc = await self._users_info()
            self.success(user_doc, cache_age=config.SECONDS_1MONTH)
        except Exception as ex:
            await self.exc(ex)


class UsersInfoPhotoApi(ApiHandler):
    @decorators.authenticated
    async def get(self, photo_id):

        try:
            if str(photo_id) == 'False' or str(photo_id) == 'True':
                raise ApiError('Nie podano odpowiedniego parametru photo_id')

            user_photo = await self.db[collections.PHOTOS].find_one({fields.MONGO_ID: ObjectId(photo_id)})

            if user_photo and 'photo' in user_photo:
                self.set_header('Content-Type', 'image/jpeg')
                self.write(b64decode(user_photo['photo']))
            else:
                self.error('Nie znaleziono zdjęcia', code=404)
        except Exception as ex:
            await self.exc(ex)
