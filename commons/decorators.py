# coding=UTF-8


from commons.constants import fields


def authenticated(method):
    def wrapper(self, *args, **kwargs):
        current_user = self.get_current_user()
        if not current_user:
            self.fail(message="Request not authenticated.", code=401)
        elif fields.USOS_PAIRED in current_user and not current_user[fields.USOS_PAIRED]:
            self.fail(message="User not paired with USOS.", code=401)
        else:
            self._user_doc = current_user
            result = method(self, *args, **kwargs)
            if result is not None:
                return result

    return wrapper
