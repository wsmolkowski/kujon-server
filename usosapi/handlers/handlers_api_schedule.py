import tornado.web

from handlers_api import BaseHandler
from usosapi.mixins.JSendMixin import JSendMixin


class ScheduleApi(BaseHandler, JSendMixin):
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

