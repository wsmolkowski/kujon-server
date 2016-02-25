import tornado.web

from handlers_api import BaseHandler


class UsersWebHandler(BaseHandler):
    def get(self):
        self.render("school.html", **self.template_data())

class UserByUserIdWebHandler(BaseHandler):
    def get(self, usos_user_id):
        data = self.template_data()
        self.render("school.html", **data)

class SchoolWebHandler(BaseHandler):
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


class CourseWebHandler(BaseHandler):
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


class ProgrammeWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, programme_id):
        data = self.template_data()
        self.render("school.html", **data)


class ProgrammesWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)

class LecturersWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)

class LecturerWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_id):
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


class FriendsWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class FriendsSuggestionsWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class SettingsWebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("settings.html", **data)


class RegulationsWebHandler(BaseHandler):
    @tornado.web.removeslash
    def get(self):
        data = self.template_data()
        self.render("regulations.html", **data)