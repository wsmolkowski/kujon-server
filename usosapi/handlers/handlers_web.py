import tornado.web

from handlers_api import BaseHandler


class MainHandler(BaseHandler):
    def get(self):
        self.render("main.html", **self.template_data())


class SchoolHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.render("school.html", **self.template_data())


class CoursesWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class CourseInfoWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, courseId):
        data = self.template_data()
        self.render("school.html", **data)


class GradesWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, courseId, termId):
        data = self.template_data()
        self.render("school.html", **data)


class TermWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, courseId):
        data = self.template_data()
        self.render("school.html", **data)


class TermsWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class ChatHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.render("chat.html", **self.template_data())


class FriendsHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = data = self.template_data()
        self.render("school.html", **data)


class FriendsSuggestionsHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = data = self.template_data()
        self.render("school.html", **data)


class SettingsHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("settings.html", **data)
