# coding=utf-8

import os
import tempfile
from configparser import RawConfigParser

from commons.enumerators import Environment


def config_path(config_name):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', config_name)


def config_parser(name):
    config = RawConfigParser(allow_no_value=True)
    if name == Environment.PRODUCTION.value:
        config.read(config_path('settings-prod.conf'))
    elif name == Environment.DEVELOPMENT.value:
        config.read(config_path('settings-dev.conf'))
    elif name == Environment.DEMO.value:
        config.read(config_path('settings-demo.conf'))
    elif name == Environment.TESTS.value:
        config.read(config_path('settings-tests.conf'))
    else:
        raise Exception('Could not return config file for unknown: {0}'.format(name))

    return config


class Config(object):
    def __init__(self, config_environment):
        if isinstance(config_environment, Environment):
            config_environment = str(config_environment)

        self.config = config_parser(config_environment)
        self.ENVIRONMENT = config_environment

        # database
        self.MONGODB_URI = self.config.get('database', 'MONGODB_URI')
        self.MONGODB_NAME = self.config.get('database', 'MONGODB_NAME')

        # application
        self.COOKIE_SECRET = self.config.get('application', 'COOKIE_SECRET')
        self.AES_SECRET = self.config.get('application', 'AES_SECRET')
        self.ENCRYPT_USOSES_KEYS = self.config.getboolean('application', 'ENCRYPT_USOSES_KEYS')
        self.PROJECT_TITLE = self.config.get('application', 'PROJECT_TITLE')
        self.DEBUG = self.config.getboolean('application', 'DEBUG')
        self.RELOAD = self.config.getboolean('application', 'RELOAD')
        self.COMPRESS_RESPONSE = self.config.getboolean('application', 'COMPRESS_RESPONSE')
        self.UNICODE = self.config.get('application', 'UNICODE')

        # proxy
        self.PROXY_URL = self.config.get('proxy', 'PROXY_URL') if self.config.get('proxy', 'PROXY_URL') else None
        self.PROXY_PORT = self.config.getint('proxy', 'PROXY_PORT') if self.config.get('proxy', 'PROXY_PORT') else None

        # social
        self.GOOGLE_CLIENT_ID = self.config.get('social', 'GOOGLE_CLIENT_ID')
        self.GOOGLE_CLIENT_SECRET = self.config.get('social', 'GOOGLE_CLIENT_SECRET')
        self.FACEBOOK_CLIENT_ID = self.config.get('social', 'FACEBOOK_CLIENT_ID')
        self.FACEBOOK_CLIENT_SECRET = self.config.get('social', 'FACEBOOK_CLIENT_SECRET')

        # deployment
        self.KUJON_SECURE_COOKIE = self.config.get('deployment', 'KUJON_SECURE_COOKIE')
        self.KUJON_MOBI_REGISTER = self.config.get('deployment', 'KUJON_MOBI_REGISTER')

        self.SITE_DOMAIN = self.config.get('deployment', 'SITE_DOMAIN')
        self.API_PORT = self.config.getint('deployment', 'API_PORT')
        self.DEPLOY_API = self.config.get('deployment', 'DEPLOY_API')
        self.WEB_VERSION = self.config.get('deployment', 'WEB_VERSION')
        self.WEB_PORT = self.config.getint('deployment', 'WEB_PORT')
        self.DEPLOY_WEB = self.config.get('deployment', 'DEPLOY_WEB')
        self.CALLBACK_URL = self.config.get('deployment', 'CALLBACK_URL')
        self.EVENT_PORT = self.config.getint('deployment', 'EVENT_PORT')
        self.DEPLOY_EVENT = self.config.get('deployment', 'DEPLOY_EVENT')
        self.LOG_LEVEL = self.config.get('deployment', 'LOG_LEVEL')

        # email
        self.SMTP_HOST = self.config.get('email', 'SMTP_HOST')
        self.SMTP_PORT = self.config.getint('email', 'SMTP_PORT')
        self.SMTP_USER = self.config.get('email', 'SMTP_USER')
        self.SMTP_EMAIL = self.config.get('email', 'SMTP_EMAIL')
        self.SMTP_PASSWORD = self.config.get('email', 'SMTP_PASSWORD')

        # ssl
        self.SSL_CERT = self.config.get('ssl', 'SSL_CERT') if self.config.get('ssl', 'SSL_CERT') else None
        self.SSL_KEY = self.config.get('ssl', 'SSL_KEY') if self.config.get('ssl', 'SSL_KEY') else None

        # administration
        if self.config.get('administration', 'LOG_DIR'):
            self.LOG_DIR = self.config.get('administration', 'LOG_DIR')
        else:
            self.LOG_DIR = tempfile.gettempdir()

        self.DEVELOPMENT = self.config.getboolean('administration', 'DEVELOPMENT')

        # notification
        self.APPLICATION_ID = self.config.get('notification', 'APPLICATION_ID')
        self.AUTHORIZATION = self.config.get('notification', 'AUTHORIZATION')
