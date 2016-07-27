# coding=UTF-8

import logging

import tornado.gen
import tornado.web
from bson import ObjectId
from bson import json_util
from tornado import gen
from tornado.escape import json_decode
from tornado.web import RequestHandler

from commons import constants
from commons.mixins.JSendMixin import JSendMixin
from crawler import email_factory

CONFIG_COOKIE_EXPIRATION = 1


class BaseHandler(RequestHandler, JSendMixin):
    SUPPORTED_METHODS = ('GET',)

    @property
    def db(self):
        return self.application.settings['db']

    @property
    def config(self):
        return self.application.settings['config']

    def get_config(self):
        return {
            'PROJECT_TITLE': self.config.PROJECT_TITLE,
            'KUJON_SECURE_COOKIE': self.config.COOKIE_SECRET,
            'API_URL': self.config.DEPLOY_API,
            'WEB_VERSION': self.config.WEB_VERSION,
        }

    @gen.coroutine
    def set_current_user(self):
        cookie = self.get_secure_cookie(constants.KUJON_SECURE_COOKIE)
        if cookie:
            cookie = json_decode(cookie)
            response = json_util.loads(cookie)
            if constants.USER_NAME not in response and constants.USER_EMAIL in response:
                response[constants.USER_NAME] = response[constants.USER_EMAIL]
            if constants.PICTURE not in response:
                response[constants.PICTURE] = None

            raise gen.Return(response)

        raise gen.Return()

    @tornado.gen.coroutine
    def get_usoses(self):
        usoses = []
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
        while (yield cursor.fetch_next):
            usos = cursor.next_object()
            usos['logo'] = self.config.DEPLOY_WEB + usos['logo']
            usoses.append(usos)

        raise tornado.gen.Return(usoses)

    @tornado.gen.coroutine
    def prepare(self):
        self._current_user = yield self.set_current_user()

    def get_current_user(self):
        return self._current_user


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        token = self.get_argument('token', default=None)
        if token:
            user = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(token)})
        else:
            user = self.get_current_user()

        if user and constants.USOS_PAIRED in user and user[constants.USOS_PAIRED]:
            self.render("app.html", **self.get_config())
        elif user and constants.USOS_PAIRED in user and not user[constants.USOS_PAIRED]:
            data = self.get_config()

            user = self.get_current_user()
            if user:
                error = yield self.db[constants.COLLECTION_EXCEPTIONS].find_one({
                    constants.USER_ID: user[constants.MONGO_ID],
                    constants.EXCEPTION_TYPE: 'authentication'
                })
                if error:
                    data['error'] = error['exception']
                else:
                    data['error'] = False

            usoses = yield self.get_usoses()
            data['usoses'] = usoses
            self.render("register.html", **data)
        else:
            self.render("index.html", **self.get_config())


class ContactHandler(BaseHandler):
    SUPPORTED_METHODS = ('POST',)

    @gen.coroutine
    def email_contact(self, subject, message):
        email_job = email_factory.email_job(
            '[KUJON.MOBI][CONTACT]: {0}'.format(subject),
            self.config.SMTP_EMAIL,
            [self.config.SMTP_EMAIL],
            '\nNowa wiadomość od użytkownik: email: {0} mongo_id: {1}\n'
            '\nwiadomość:\n{2}\n'.format(self.get_current_user()[constants.USER_EMAIL],
                                         self.get_current_user()[constants.MONGO_ID],
                                         message)
        )

        job_id = yield self.db[constants.COLLECTION_EMAIL_QUEUE].insert(email_job)
        raise gen.Return(job_id)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        try:
            subject = self.get_argument('subject', default=None)
            message = self.get_argument('message', default=None)

            logging.info('received contact request from user:{0} subject: {1} message: {2}'.format(
                self.get_current_user()[constants.MONGO_ID], subject, message))

            job_id = yield self.email_contact(subject, message)

            self.success(data='Wiadomość otrzymana. Numer referencyjny: {0}'.format(str(job_id)))
        except Exception as ex:
            logging.exception(ex)
            self.error(message=ex.message, data=ex.message, code=501)


class DisclaimerHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("disclaimer.html", **self.get_config())


class DefaultErrorHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.get_config()
        data['MESSAGE'] = '404 - Strona o podanym adresie nie istnieje.'
        self.render('error.html', **data)
