import tornado.web

from handlers_api import BaseHandler


class Main_WebHandler(BaseHandler):
    def get(self):
        self.render("main.html", **self.template_data())


class Users_WebHandler(BaseHandler):
    def get(self):
        self.render("school.html", **self.template_data())

class UserByUserId_WebHandler(BaseHandler):
    def get(self, usos_user_id):
        data = self.template_data()
        self.render("school.html", **data)

class School_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.render("school.html", **self.template_data())


class Courses_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class CourseEdition_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):
        data = self.template_data()
        self.render("school.html", **data)


class Grades_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, course_id, term_id):
        data = self.template_data()
        self.render("school.html", **data)


class Programme_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, programme_id):
        data = self.template_data()
        self.render("school.html", **data)


class Programmes_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)

class Lecturers_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)

class Lecturer_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_id):
        data = self.template_data()
        self.render("school.html", **data)

class Term_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, term_id):
        data = self.template_data()
        self.render("school.html", **data)


class Terms_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)

class Schedule_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class Friends_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class FriendsSuggestions_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("school.html", **data)


class Settings_WebHandler(BaseHandler):
    @tornado.web.removeslash
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        self.render("settings.html", **data)


class Regulations_WebHandler(BaseHandler):
    @tornado.web.removeslash
    def get(self):
        data = self.template_data()
        self.render("regulations.html", **data)