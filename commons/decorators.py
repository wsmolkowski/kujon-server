
import constants
import functools
from tornado.web import HTTPError


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_user():
            if self.request.method in ("GET", "POST", "HEAD"):
                user_doc = self.get_current_user()

                if not user_doc:
                    # usos_id = self.get_argument(constants.USOS_ID, default=None, strip=True)
                    # mobile_id = self.get_argument(constants.MOBILE_ID, default=None, strip=True)
                    atk = self.get_argument(constants.ACCESS_TOKEN_KEY, default=None, strip=True)
                    ats = self.get_argument(constants.ACCESS_TOKEN_SECRET, default=None, strip=True)

                    user_doc = self.dao.get_user_by_tokens(atk, ats)

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