# coding=UTF-8

import tornado.gen
import tornado.web
from bson import json_util
from tornado.escape import json_decode
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

    def get_current_user(self):
        cookie = self.get_secure_cookie(constants.KUJON_SECURE_COOKIE)
        if not cookie:
            return cookie

        user = json_decode(cookie)
        user = json_util.loads(user)

        return user

    @tornado.gen.coroutine
    def get_usoses(self):
        usoses = []
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': True})
        while (yield cursor.fetch_next):
            usos = cursor.next_object()
            usos['logo'] = settings.DEPLOY_WEB + usos['logo']
            usoses.append(usos)

        raise tornado.gen.Return(usoses)


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()
        if not user:
            self.render("index.html", **CONFIG)
            return

        if user and constants.USOS_PAIRED in user and user[constants.USOS_PAIRED]:
            self.render("app.html", **CONFIG)
        elif user and constants.USOS_PAIRED in user and not user[constants.USOS_PAIRED]:
            self.redirect('/rejestracja')
        else:
            self.render("index.html", **CONFIG)


class ContactHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("contact.html", **CONFIG)


class DisclaimerHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("disclaimer.html", **CONFIG)


class RegisterHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()

        if not user:
            self.redirect("index.html", **CONFIG)
            return

        if user and constants.USOS_PAIRED in user and user[constants.USOS_PAIRED]:
            self.render("app.html", **CONFIG)
        elif user and constants.USOS_PAIRED in user and not user[constants.USOS_PAIRED]:
            data = CONFIG
            usoses = yield self.get_usoses()
            data['usoses'] = usoses
            self.render("register.html", **CONFIG)
        else:
            self.redirect("/")


class DefaultErrorHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = CONFIG
        data['MESSAGE'] = '404 - Strona o podanym adresie nie istnieje.'
        self.render('error.html', **data)
