import functools

import tornado.gen

from commons import constants, settings


def authenticated(method):
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        current_user = yield self.get_current_user()
        if not current_user:
            self.fail("Request not authenticated.")
            return
        else:
            self.user_doc = current_user
            result = method(self, *args, **kwargs)  # updates
            if result is not None:
                yield result
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
