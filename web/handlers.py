# coding=UTF-8

import logging

import tornado.gen
import tornado.web
from bson import ObjectId
from bson import json_util
from tornado import gen
from tornado.escape import json_decode, utf8
from tornado.web import RequestHandler

from commons import constants, settings
from commons.mixins.JSendMixin import JSendMixin

CONFIG_COOKIE_EXPIRATION = 1

CONFIG = {
    'PROJECT_TITLE': settings.PROJECT_TITLE,
    'KUJON_SECURE_COOKIE': constants.KUJON_SECURE_COOKIE,
    'API_URL': settings.DEPLOY_API,
    'WEB_VERSION': settings.WEB_VERSION,
}


class BaseHandler(RequestHandler, JSendMixin):
    @property
    def db(self):
        return self.application.settings['db']

    @gen.coroutine
    def set_current_user(self):
        cookie = self.get_secure_cookie(constants.KUJON_SECURE_COOKIE)
        if cookie:
            cookie = json_decode(cookie)
            response = json_util.loads(cookie)
            raise gen.Return(response)

        raise gen.Return(None)

    @tornado.gen.coroutine
    def get_usoses(self):
        usoses = []
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
        while (yield cursor.fetch_next):
            usos = cursor.next_object()
            usos['logo'] = settings.DEPLOY_WEB + usos['logo']
            usoses.append(usos)

        raise tornado.gen.Return(usoses)

    @tornado.gen.coroutine
    def prepare(self):
        logging.info('KUJON_SECURE_COOKIE {0}'.format(self.get_secure_cookie(constants.KUJON_SECURE_COOKIE)))

        self.current_user = yield self.set_current_user()

    def get_current_user(self):
        return self.current_user


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        token = self.get_argument('token', default=None, strip=True)
        if token:
            user = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: ObjectId(token)})
        else:
            user = self.get_current_user()

        if user and constants.USOS_PAIRED in user and user[constants.USOS_PAIRED]:
            self.render("app.html", **CONFIG)
        elif user and constants.USOS_PAIRED in user and not user[constants.USOS_PAIRED]:
            data = CONFIG
            usoses = yield self.get_usoses()
            data['usoses'] = usoses
            self.render("register.html", **CONFIG)
        else:
            self.render("index.html", **CONFIG)

        self.set_header("Location", utf8(settings.DEPLOY_WEB))


class ContactHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("contact.html", **CONFIG)


class DisclaimerHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("disclaimer.html", **CONFIG)


class DefaultErrorHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = CONFIG
        data['MESSAGE'] = '404 - Strona o podanym adresie nie istnieje.'
        self.render('error.html', **data)
