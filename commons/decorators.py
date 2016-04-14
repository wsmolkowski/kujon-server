import functools

from tornado.web import HTTPError

import constants


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_user():
            if self.request.method in ("GET", "POST", "HEAD"):
                user_doc = self.get_current_user()

                if not user_doc:
                    header_email = self.request.headers.get(constants.MOBILE_X_HEADER_EMAIL, False)
                    header_token = self.request.headers.get(constants.MOBILE_X_HEADER_TOKEN, False)

                    user_doc = self.dao[constants.COLLECTION_USERS].find_one({
                        constants.USOS_PAIRED: True,
                        constants.USER_EMAIL: header_email,
                        constants.MOBI_TOKEN: header_token,
                    })

                if not user_doc or not user_doc['usos_paired']:
                    self.fail("Request not authenticated.")
                else:
                    self.user_doc = user_doc
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
