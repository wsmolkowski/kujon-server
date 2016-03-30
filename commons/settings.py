import os
from ConfigParser import RawConfigParser

config = RawConfigParser(allow_no_value=True)
PRODUCTION = False


def parent_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if PRODUCTION:
    config.read(os.path.join(parent_dir(), 'config', 'settings-prod.conf'))
else:
    config.read(os.path.join(parent_dir(), 'config', 'settings-dev.conf'))

MONGODB_URI = config.get('database', 'MONGODB_URI')
MONGODB_NAME = config.get('database', 'MONGODB_NAME')

COOKIE_SECRET = config.get('application', 'COOKIE_SECRET')
AES_SECRET = config.get('application', 'AES_SECRET')

PROJECT_TITLE = config.get('application', 'PROJECT_TITLE')
DEBUG = config.getboolean('application', 'DEBUG')
RELOAD = config.getboolean('application', 'RELOAD')
COMPRESS_RESPONSE = config.getboolean('application', 'COMPRESS_RESPONSE')
UNICODE = config.get('application', 'UNICODE')

PROXY_URL = config.get('proxy', 'PROXY_URL') if config.get('proxy', 'PROXY_URL') else None
PROXY_PORT = config.getint('proxy', 'PROXY_PORT') if config.get('proxy', 'PROXY_PORT') else None

GOOGLE_CLIENT_ID = config.get('social', 'GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config.get('social', 'GOOGLE_CLIENT_SECRET')
FACEBOOK_CLIENT_ID = config.get('social', 'FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = config.get('social', 'FACEBOOK_CLIENT_SECRET')

SITE_DOMAIN = config.get('deployment', 'SITE_DOMAIN')
API_PORT = config.getint('deployment', 'API_PORT')
DEPLOY_API = config.get('deployment', 'DEPLOY_API')

WEB_PORT = config.getint('deployment', 'WEB_PORT')
DEPLOY_WEB = config.get('deployment', 'DEPLOY_WEB')
CALLBACK_URL = config.get('deployment', 'CALLBACK_URL')
LOGIN_URL = config.get('deployment', 'LOGIN_URL')

SMTP_HOST = config.get('email', 'SMTP_HOST')
SMTP_PORT = config.getint('email', 'SMTP_PORT')
SMTP_USER = config.get('email', 'SMTP_USER')
SMTP_PASSWORD = config.get('email', 'SMTP_PASSWORD')

SSL_CERT = config.get('ssl', 'SSL_CERT') if config.get('ssl', 'SSL_CERT') else None
SSL_KEY = config.get('ssl', 'SSL_KEY') if config.get('ssl', 'SSL_KEY') else None

LOG_DIR = config.get('administration', 'LOG_DIR')
