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
    ARCHIVE_USER = 'archive_user'
    INITIAL_USER_CRAWL = 'initial_user_crawl'
    REFRESH_USER_CRAWL = 'refresh_user_crawl'
    UPDATE_USER_CRAWL = 'update_user_crawl'
    SUBSCRIBE_USOS = 'subscribe_usos'
    UNSUBSCRIBE_USOS = 'unsubscribe_usos'
    SUBSCRIPTION_EVENT = 'subscription_event'


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
