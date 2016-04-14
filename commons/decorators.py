import functools

from tornado.web import HTTPError


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_user():
            if self.request.method in ("GET", "POST", "HEAD"):
                self.fail("Request not authenticated.")
                return
            raise HTTPError(403)
        else:
            self.user_doc = self.get_current_user()

        return method(self, *args, **kwargs)

    return wrapper


def application_json(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json')

        return method(self, *args, **kwargs)

    return wrapper
