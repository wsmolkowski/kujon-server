# coding=UTF-8

from commons import constants


def authenticated(method):
    def wrapper(self, *args, **kwargs):
        current_user = self.get_current_user()
        if not current_user:
            self.fail(message="Request not authenticated.", code=401)
        elif constants.USOS_PAIRED in current_user and not current_user[constants.USOS_PAIRED]:
            self.fail(message="User not paired with USOS.", code=401)
        else:
            self._user_doc = current_user
            result = method(self, *args, **kwargs)
            if result is not None:
                return result

    return wrapper
