# coding=UTF-8

import tornado.gen
import tornado.web

from apidao import ApiDaoHandler
from base import BaseHandler
from commons import constants, settings, decorators


class LecturersApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        try:
            lecturers_doc = yield self.api_lecturers()
            if not lecturers_doc:
                self.error("Poczekaj, szukamy informacji o Twoich nauczycielach.")
            else:
                self.success(lecturers_doc, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)


class LecturerByIdApi(BaseHandler, ApiDaoHandler):
    @decorators.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_info_id):

        try:
            user_info_doc = yield self.api_lecturer(user_info_id)

            # if user has photo
            if constants.HAS_PHOTO in user_info_doc and user_info_doc[constants.HAS_PHOTO]:
                photo_doc = yield self.api_photo(user_info_doc[constants.ID])
                user_info_doc[constants.HAS_PHOTO] = settings.DEPLOY_API + '/users_info_photos/' + str(photo_doc[constants.MONGO_ID])

            self.success(user_info_doc, cache_age=2592000)
        except Exception, ex:
            yield self.exc(ex)
