import tornado.gen


def authenticated(method):
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        current_user = yield self.get_current_user()
        if not current_user:
            self.fail(message="Request not authenticated.", code=401)
            return
        else:
            if not current_user["usos_paired"]:
                self.fail(message="User not paired with USOS.", code=401)
                return
            self.user_doc = current_user
            result = method(self, *args, **kwargs)
            if result is not None:
                yield result
    return wrapper

