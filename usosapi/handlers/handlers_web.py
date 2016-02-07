import tornado.web

from handlers_api import BaseHandler


class MainHandler(BaseHandler):
    def get(self):
        self.render("main.html", **self.template_data())


class UsersHandler(BaseHandler):
    def get(self):
        self.render("school.html", **self.template_data())

class UserHandlerByUserId(BaseHandler):
    def get(self, usos_user_id):
        data = self.template_data()
        self.render("school.html", **data)


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
    def get(self, course_id):
        data = self.template_data()
        self.render("school.html", **data)


class GradesWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):
        data = self.template_data()
        self.render("school.html", **data)


class TermWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):
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

class ScheduleWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class FriendsHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class FriendsSuggestionsHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class SettingsHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("settings.html", **data)
