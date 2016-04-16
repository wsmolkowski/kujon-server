import functools

from tornado.web import HTTPError

from commons import constants, settings


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


def extra_headers(cache_age=None):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if settings.DEVELOPMENT:
                self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            else:
                if not cache_age:
                    self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                else:
                    self.set_header('Cache-Control', 'public, max-age={0}'.format(cache_age))

            self.set_header('Content-Type', 'application/json; charset={0}'.format(constants.ENCODING))

            return method(self, *args, **kwargs)

        return wrapper

    return decorator
