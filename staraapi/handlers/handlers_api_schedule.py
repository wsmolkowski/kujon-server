import tornado.web

from handlers_api import BaseHandler


class ScheduleApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        #parameters = yield self.get_parameters()

        terms = []
        terms_doc = []

        if not terms_doc:
            self.error("Please hold on we are looking your schedule..")
        else:
            self.success(terms_doc)

