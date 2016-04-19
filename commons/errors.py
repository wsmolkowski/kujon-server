import json

import utils


class Error(Exception):
    """Base error for this module."""
    pass


class HttpError(Error):
    """HTTP data was invalid or unexpected."""

    def __init__(self, resp, content, uri=None, parameters=None):
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
        reason = self._get_reason()
        reason.update(self.extras)
        reason['resp'] = self.resp
        reason['status'] = self.resp.status
        reason['uri'] = self.uri
        reason['parameters'] = self.parameters

        return json.dumps(utils.serialize(reason))

    def append(self, key, value):
        self.extras[key] = value

    __str__ = __repr__


class UsosClientError(HttpError):
    """USOS exceptions"""
    pass


class UsosAsyncError(HttpError):
    """USOS exceptions"""
    pass
