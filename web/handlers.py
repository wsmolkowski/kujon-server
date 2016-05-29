# coding=UTF-8

import tornado.gen
import tornado.web
from bson import json_util
from tornado import gen
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


def authenticated(method):
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        current_user = yield self.get_current_user()
        if not current_user:
            self.fail(message="Request not authenticated.", code=401)
            return
        else:
            self.user_doc = current_user
            result = method(self, *args, **kwargs)
            if result is not None:
                yield result

    return wrapper


class BaseHandler(RequestHandler, JSendMixin):
    @property
    def db(self):
        return self.application.settings['db']

    @gen.coroutine
    def get_current_user(self):
        response = None
        if hasattr(self, 'user_doc') and self.user_doc:
            response = self.user_doc

        if not response:
            cookie = self.get_secure_cookie(constants.KUJON_SECURE_COOKIE)
            if cookie:
                cookie = json_decode(cookie)
                response = json_util.loads(cookie)

        if not response:
            header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
            header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

            if header_email and header_token:
                token_exists = yield self.find_token(header_email)

                if token_exists:
                    user_doc = yield self.current_user(header_email)
                    response = user_doc

        raise gen.Return(response)

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
        user = yield self.get_current_user()
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
    @authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        user = yield self.get_current_user()

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


class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("login.html", **CONFIG)


class DefaultErrorHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = CONFIG
        data['MESSAGE'] = '404 - Strona o podanym adresie nie istnieje.'
        self.render('error.html', **data)
