import tornado.gen


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

