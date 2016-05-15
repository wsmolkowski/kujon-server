import json

import constants


class Error(Exception):
    """Base error for this module."""
    pass


class ApiError(Exception):
    """Api Errors"""

    def __init__(self, msg, parameters=[]):
        self.msg = msg.encode(constants.ENCODING)
        if not isinstance(parameters, list) or not isinstance(parameters, tuple):
            self.parameters = [parameters]
        else:
            self.parameters = parameters

    def data(self):
        return {
            'message': self.msg,
            'parameters': self.parameters
        }

    def message(self):
        if self.parameters and len(self.parameters) > 1:
            return "{0} - {1}".format(self.msg, "; ".join(self.parameters))
        else:
            return self.msg

    def __repr__(self):
        return self.message()

    __str__ = __repr__


class HttpError(Error):
    def __init__(self, resp, content, uri=None, parameters=[]):
        self.resp = resp
        self.content = content
        self.uri = uri
        self.parameters = parameters
        self.extras = dict()

    def _get_reason(self):
        """Calculate the reason for the error from the response content."""
        try:
            return json.loads(self.content)
        except (ValueError, KeyError):
            return {
                'content': self.content
            }

    def __repr__(self):
        return str(self._message())

    def _message(self):
        reason = self._get_reason()
        reason.update(self.extras)
        reason['resp'] = self.resp
        reason['status'] = self.resp.status
        reason['uri'] = self.uri
        reason['parameters'] = self.parameters

        return reason

    @property
    def message(self):
        return self._message()

    def append(self, key, value):
        self.extras[key] = value

    __str__ = __repr__


class UsosClientError(HttpError):
    """USOS exceptions"""
    pass


class UsosAsyncError(HttpError):
    """USOS exceptions"""
    pass


class AuthenticationError(Exception):
    """USOS exceptions"""
    pass


class CrawlerException(Exception):
    """Crawler Exceptions"""
    pass
