# coding=UTF-8

from enum import Enum


class Abstract(Enum):
    def __str__(self):
        return self.value


class JobStatus(Abstract):
    PENDING = 'pending'
    START = 'start'
    FINISH = 'finish'
    FAIL = 'fail'


class JobType(Abstract):
    INITIAL_USER_CRAWL = 'initial_user_crawl'
    REFRESH_USER_CRAWL = 'refresh_user_crawl'
    SUBSCRIBE_USOS = 'subscribe_usos'


class Environment(Abstract):
    PRODUCTION = 'production'
    DEVELOPMENT = 'development'
    DEMO = 'demo'
    TESTS = 'tests'


class ExceptionTypes(Abstract):
    DEFAULT = 'default'
    DAO = 'dao'
    API = 'api'
    AUTHENTICATION = 'authentication'
    CRAWLER = 'crawler'
    EVENT = 'event'
    UNKNOWN = 'unknown'


class UserTypes(Abstract):
    GOOGLE = 'GOOGLE'
    FACEBOOK = 'FACEBOOK'
    WWW = 'WWW'
    EMAIL = 'EMAIL'


class UploadFileStatus(Abstract):
    NEW = 'PENDING'
    DELETED = 'DELETED'
    INVALID = 'INVALID'
    STORED = 'STORED'
