# coding=UTF-8

import logging

import tornado.web
from bson import ObjectId
from cryptography.fernet import InvalidToken

from commons import constants
from commons.enumerators import ExceptionTypes
from commons.handlers import AbstractHandler


class BaseHandler(AbstractHandler):
    SUPPORTED_METHODS = ('GET',)

    def get_config(self):
        return {
            'PROJECT_TITLE': self.config.PROJECT_TITLE,
            'KUJON_SECURE_COOKIE': self.config.COOKIE_SECRET,
            'API_URL': self.config.DEPLOY_API,
            'WEB_VERSION': self.config.WEB_VERSION,
            'DEPLOY_WEB': self.config.DEPLOY_WEB,
        }

    async def _prepare_user(self):
        user_doc = None
        cookie_encrypted = self.get_secure_cookie(self.config.KUJON_SECURE_COOKIE)
        if cookie_encrypted:
            try:
                cookie_decrypted = self.aes.decrypt(cookie_encrypted)
                user_doc = await self.db[constants.COLLECTION_USERS].find_one(
                    {constants.MONGO_ID: ObjectId(cookie_decrypted.decode())})
            except InvalidToken as ex:
                logging.exception(ex)
                self.clear_cookie(self.config.KUJON_SECURE_COOKIE)

            if not user_doc:
                self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
                return

            if constants.USER_NAME not in user_doc and constants.USER_EMAIL in user_doc:
                user_doc[constants.USER_NAME] = user_doc[constants.USER_EMAIL]

            user_doc[constants.PICTURE] = None

            if constants.USOS_USER_ID in user_doc:
                user_info = await self.db[constants.COLLECTION_USERS_INFO].find_one(
                    {constants.ID: user_doc[constants.USOS_USER_ID], constants.USOS_ID: user_doc[constants.USOS_ID]})

                if not user_info:
                    user_doc[constants.PICTURE] = None
                else:
                    if constants.PHOTO_URL in user_info:
                        user_doc[constants.PICTURE] = user_info[constants.PHOTO_URL]
                    elif constants.GOOGLE in user_doc:
                        user_doc[constants.PICTURE] = user_doc[constants.GOOGLE][constants.GOOGLE_PICTURE]
                    elif constants.FACEBOOK in user_doc:
                        user_doc[constants.PICTURE] = user_doc[constants.FACEBOOK][constants.FACEBOOK_PICTURE]
                    else:
                        user_doc[constants.PICTURE] = None

            return user_doc
        return


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    async def get(self):

        token = self.get_argument('token', default=None)
        if token:
            user_id = self.aes.decrypt(token.encode()).decode()
            user_doc = await self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: ObjectId(user_id)})

            self.reset_user_cookie(user_doc[constants.MONGO_ID])
            self.redirect(self.config.DEPLOY_WEB)
            return
        else:
            user_doc = self.get_current_user()

        if user_doc and constants.USOS_PAIRED in user_doc and user_doc[constants.USOS_PAIRED]:
            self.render("app.html", **self.get_config())
        elif user_doc and constants.USOS_PAIRED in user_doc and not user_doc[constants.USOS_PAIRED]:
            data = self.get_config()

            if user_doc:
                error = await self.db[constants.COLLECTION_EXCEPTIONS].find_one({
                    constants.USER_ID: user_doc[constants.MONGO_ID],
                    'exception_type': ExceptionTypes.AUTHENTICATION.value
                })
                if error:
                    data['error'] = error['exception']
                else:
                    data['error'] = False

            data['usoses'] = await self.get_usoses()
            self.render("register.html", **data)
        else:
            self.render("index.html", **self.get_config())


class ContactHandler(BaseHandler):
    SUPPORTED_METHODS = ('POST',)

    @tornado.web.asynchronous
    async def post(self):
        try:
            subject = self.get_argument('subject', default=None)
            message = self.get_argument('message', default=None)

            logging.info('received contact request from user:{0} subject: {1} message: {2}'.format(
                self.get_current_user()[constants.MONGO_ID], subject, message))

            job_id = await self.email_contact(subject, message, self.get_current_user()[constants.USER_EMAIL],
                                              self.getUserId(return_object_id=True))

            self.success(data='Wiadomość otrzymana. Numer referencyjny: {0}'.format(str(job_id)))
        except Exception as ex:
            logging.exception(ex)
            self.error(message=ex.message, data=ex.message, code=501)


class LoginHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET',)

    @tornado.web.asynchronous
    async def get(self):
        self.render("login.html", **self.get_config())


class RegisterHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET',)

    @tornado.web.asynchronous
    async def get(self):
        self.render("login_register.html", **self.get_config())


class DisclaimerHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("disclaimer.html", **self.get_config())
