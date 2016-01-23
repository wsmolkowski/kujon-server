from datetime import datetime

import motor
import tornado.web

import settings
from handlers_api import BaseHandler


class MainHandler(BaseHandler):
    def get(self):
        data = {
            'PROJECT_TITLE': settings.PROJECT_TITLE
        }

        self.render("main.html", **data)


class SchoolHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = {
            'PROJECT_TITLE': settings.PROJECT_TITLE
        }
        self.render("school.html", **data)


class CoursesWebHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = {
            'PROJECT_TITLE': settings.PROJECT_TITLE
        }
        self.render("school-courses.html", **data)


class GradesWebHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = {
            'PROJECT_TITLE': settings.PROJECT_TITLE
        }
        self.render("school-grades.html", **data)


class ChatHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = {
            'PROJECT_TITLE': settings.PROJECT_TITLE
        }
        self.render("chat.html", **data)


class FriendsHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = {
            'PROJECT_TITLE': settings.PROJECT_TITLE
        }
        self.render("friends.html", **data)


class SettingsHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = {
            'PROJECT_TITLE': settings.PROJECT_TITLE
        }
        self.render("settings.html", **data)