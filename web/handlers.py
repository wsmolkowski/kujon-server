# coding=UTF-8

import logging

import tornado.web
from bson import ObjectId

from commons import constants
from commons.enumerators import ExceptionTypes
from commons.handlers import AbstractHandler
from crawler import email_factory

CONFIG_COOKIE_EXPIRATION = 1


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

    async def set_current_user(self):
        cookie_encrypted = self.get_secure_cookie(self.config.KUJON_SECURE_COOKIE)
        if cookie_encrypted:
            cookie_decrypted = self.aes.decrypt(cookie_encrypted)
            response = await self.db[constants.COLLECTION_USERS].find_one(
                {constants.MONGO_ID: ObjectId(cookie_decrypted.decode())})

            if constants.USER_NAME not in response and constants.USER_EMAIL in response:
                response[constants.USER_NAME] = response[constants.USER_EMAIL]

            response[constants.PICTURE] = None

            if constants.USOS_USER_ID in response:
                user_info = await self.db[constants.COLLECTION_USERS_INFO].find_one(
                    {constants.ID: response[constants.USOS_USER_ID], constants.USOS_ID: response[constants.USOS_ID]})
                if constants.PHOTO_URL in user_info:
                    response[constants.PICTURE] = user_info[constants.PHOTO_URL]
                elif constants.GOOGLE in response:
                    response[constants.PICTURE] = response[constants.GOOGLE][constants.GOOGLE_PICTURE]
                elif constants.FACEBOOK in response:
                    response[constants.PICTURE] = response[constants.FACEBOOK][constants.FACEBOOK_PICTURE]

            return response
        return None

    async def prepare(self):
        self._current_user = await self.set_current_user()

    def get_current_user(self):
        return self._current_user


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    async def get(self):

        token = self.get_argument('token', default=None)
        if token:
            user = await self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(token)})
        else:
            user = self.get_current_user()

        if user and constants.USOS_PAIRED in user and user[constants.USOS_PAIRED]:
            self.render("app.html", **self.get_config())
        elif user and constants.USOS_PAIRED in user and not user[constants.USOS_PAIRED]:
            data = self.get_config()

            user = self.get_current_user()
            if user:
                error = await self.db[constants.COLLECTION_EXCEPTIONS].find_one({
                    constants.USER_ID: user[constants.MONGO_ID],
                    'exception_type': ExceptionTypes.AUTHENTICATION.value
                })
                if error:
                    data['error'] = error['exception']
                else:
                    data['error'] = False

            usoses = await self.get_usoses()
            data['usoses'] = usoses
            self.render("register.html", **data)
        else:
            self.render("index.html", **self.get_config())


class ContactHandler(BaseHandler):
    SUPPORTED_METHODS = ('POST',)

    async def email_contact(self, subject, message):
        email_job = email_factory.email_job(
            '[KUJON.MOBI][CONTACT]: {0}'.format(subject),
            self.config.SMTP_EMAIL,
            [self.config.SMTP_EMAIL],
            '\nNowa wiadomość od użytkownik: email: {0} mongo_id: {1}\n'
            '\nwiadomość:\n{2}\n'.format(self.get_current_user()[constants.USER_EMAIL],
                                         self.get_current_user()[constants.MONGO_ID],
                                         message)
        )

        job_id = await self.db[constants.COLLECTION_EMAIL_QUEUE].insert(email_job)
        return job_id

    @tornado.web.asynchronous
    async def post(self):
        try:
            subject = self.get_argument('subject', default=None)
            message = self.get_argument('message', default=None)

            logging.info('received contact request from user:{0} subject: {1} message: {2}'.format(
                self.get_current_user()[constants.MONGO_ID], subject, message))

            job_id = await self.email_contact(subject, message)

            self.success(data='Wiadomość otrzymana. Numer referencyjny: {0}'.format(str(job_id)))
        except Exception as ex:
            logging.exception(ex)
            self.error(message=ex.message, data=ex.message, code=501)


class DisclaimerHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("disclaimer.html", **self.get_config())

