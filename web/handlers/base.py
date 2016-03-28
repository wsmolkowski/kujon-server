import tornado.gen
from commons.mixins.JSendMixin import JSendMixin
from commons import handlers


class BaseHandler(handlers.CommonHandler, JSendMixin):
    @property
    def db(self):
        return self.application.db


class DefaultErrorHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.template_data()
        data['message'] = 'Przepraszamy ale strona o podanym adresie nie istnieje.'
        self.render('error.html', **data)
