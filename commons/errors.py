import json


class Error(Exception):
    """Base error for this module."""
    pass


class HttpError(Error):
    """HTTP data was invalid or unexpected."""

    def __init__(self, resp, content, uri=None):
        self.resp = resp
        self.content = content
        self.uri = uri

    def _get_reason(self):
        """Calculate the reason for the error from the response content."""
        reason = self.resp.reason
        try:
            data = json.loads(self.content)
            reason = data['error']['message']
        except (ValueError, KeyError):
            pass
        if reason is None:
            reason = ''
        return reason

    def __repr__(self):
        if self.uri:
            return '<HttpError %s when requesting %s returned "%s">' % (
                self.resp.status, self.uri, self._get_reason().strip())
        else:
            return '<HttpError %s "%s">' % (self.resp.status, self._get_reason())

    __str__ = __repr__


class UsosError(HttpError):
    """USOS exceptions"""
    pass
