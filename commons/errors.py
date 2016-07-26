# coding=utf-8


class ApiError(Exception):
    pass


class AuthenticationError(Exception):
    """USOS exceptions"""
    pass


class CrawlerException(Exception):
    """Crawler Exceptions"""
    pass


class OneSignalError(Exception):
    """OneSignal exceptions"""
    pass


class DaoError(Exception):
    """Dao Mongo exceptions"""
    pass


class CallerError(Exception):
    """Base error for this module."""
    pass
