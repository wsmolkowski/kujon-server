# coding=UTF-8

import logging

from bson import ObjectId
from cryptography.fernet import InvalidToken

from commons.constants import fields, collections
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
            'MESSAGE': False
        }

    async def _prepare_user(self):
        user_doc = None
        cookie_encrypted = self.get_secure_cookie(self.config.KUJON_SECURE_COOKIE)
        if cookie_encrypted:
            try:
                cookie_decrypted = self.aes.decrypt(cookie_encrypted)
                user_doc = await self.db[collections.USERS].find_one(
                    {fields.MONGO_ID: ObjectId(cookie_decrypted.decode())})
            except InvalidToken as ex:
                logging.exception(ex)
                self.clear_cookie(self.config.KUJON_SECURE_COOKIE)

            if not user_doc:
                self.clear_cookie(self.config.KUJON_SECURE_COOKIE, domain=self.config.SITE_DOMAIN)
                return

            if fields.USER_NAME not in user_doc and fields.USER_EMAIL in user_doc:
                user_doc[fields.USER_NAME] = user_doc[fields.USER_EMAIL]

            user_doc[fields.PICTURE] = None

            if fields.USOS_USER_ID in user_doc:
                user_info = await self.db[collections.USERS_INFO].find_one(
                    {fields.ID: user_doc[fields.USOS_USER_ID], fields.USOS_ID: user_doc[fields.USOS_ID]})

                if not user_info:
                    user_doc[fields.PICTURE] = None
                else:
                    if fields.PHOTO_URL in user_info:
                        user_doc[fields.PICTURE] = user_info[fields.PHOTO_URL]
                    elif fields.GOOGLE in user_doc:
                        user_doc[fields.PICTURE] = user_doc[fields.GOOGLE][fields.GOOGLE_PICTURE]
                    elif fields.FACEBOOK in user_doc:
                        user_doc[fields.PICTURE] = user_doc[fields.FACEBOOK][fields.FACEBOOK_PICTURE]
                    else:
                        user_doc[fields.PICTURE] = None

            return user_doc
        return


class MainHandler(BaseHandler):
    async def get(self):

        token = self.get_argument('token', default=None)
        if token:
            user_id = self.aes.decrypt(token.encode()).decode()
            user_doc = await self.db[collections.USERS].find_one(
                {fields.MONGO_ID: ObjectId(user_id)})

            self.reset_user_cookie(user_doc[fields.MONGO_ID])
            self.redirect(self.config.DEPLOY_WEB)
            return
        else:
            user_doc = self.get_current_user()

        if user_doc and fields.USOS_PAIRED in user_doc and user_doc[fields.USOS_PAIRED]:
            self.render("app.html", **self.get_config())
        elif user_doc and fields.USOS_PAIRED in user_doc and not user_doc[fields.USOS_PAIRED]:
            data = self.get_config()

            if user_doc:
                error = await self.db[collections.EXCEPTIONS].find_one({
                    fields.USER_ID: user_doc[fields.MONGO_ID],
                    'exception_type': ExceptionTypes.AUTHENTICATION.value
                })
                if error:
                    data['error'] = error['exception']
                else:
                    data['error'] = False

            data['usoses'] = await self.db_all_usoses()
            self.render("register.html", **data)
        else:
            self.render("index.html", **self.get_config())


class ContactHandler(BaseHandler):
    SUPPORTED_METHODS = ('POST',)

    async def post(self):
        try:
            subject = self.get_argument('subject', default=None)
            message = self.get_argument('message', default=None)

            if not subject or not message:
                self.error(message='Nie przekazano wymaganych parametrów.')
            else:
                logging.debug('received contact request from user:{0} subject: {1} message: {2}'.format(
                    self.getUserId(), subject, message))

                message_id = await self.email_contact(subject, message, self.get_current_user()[fields.USER_EMAIL])

                self.success(data='Wiadomość otrzymana. Numer referencyjny: {0}'.format(str(message_id)))
        except Exception as ex:
            logging.exception(ex)
            self.error(message=ex.message, data=ex.message, code=501)


class LoginHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET',)

    async def get(self):
        token = self.get_argument('token', default=None)
        if token:
            config = self.get_config()
            config['MESSAGE'] = 'Udało Ci się potwierdzić założenie konta. Teraz możesz logować się przy pomocy email.'
            self.render("login.html", **config)
        else:
            self.render("login.html", **self.get_config())


class RegisterHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET',)

    async def get(self):
        self.render("login_register.html", **self.get_config())


class DisclaimerHandler(BaseHandler):
    def get(self):
        self.render("disclaimer.html", **self.get_config())
