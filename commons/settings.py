import os
from ConfigParser import RawConfigParser

CONFIG = RawConfigParser(allow_no_value=True)
PRODUCTION = False


def parent_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PRODUCTION:
    CONFIG.read(os.path.join(parent_dir(), 'config', 'settings-prod.conf'))
else:
    CONFIG.read(os.path.join(parent_dir(), 'config', 'settings-dev.conf'))

MONGODB_URI = CONFIG.get('database', 'MONGODB_URI')
MONGODB_NAME = CONFIG.get('database', 'MONGODB_NAME')

COOKIE_SECRET = CONFIG.get('application', 'COOKIE_SECRET')
AES_SECRET = CONFIG.get('application', 'AES_SECRET')

PROJECT_TITLE = CONFIG.get('application', 'PROJECT_TITLE')
DEBUG = CONFIG.getboolean('application', 'DEBUG')
RELOAD = CONFIG.getboolean('application', 'RELOAD')
COMPRESS_RESPONSE = CONFIG.getboolean('application', 'COMPRESS_RESPONSE')
UNICODE = CONFIG.get('application', 'UNICODE')

PROXY_URL = CONFIG.get('proxy', 'PROXY_URL') if CONFIG.get('proxy', 'PROXY_URL') else None
PROXY_PORT = CONFIG.getint('proxy', 'PROXY_PORT') if CONFIG.get('proxy', 'PROXY_PORT') else None

GOOGLE_CLIENT_ID = CONFIG.get('social', 'GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = CONFIG.get('social', 'GOOGLE_CLIENT_SECRET')
FACEBOOK_CLIENT_ID = CONFIG.get('social', 'FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = CONFIG.get('social', 'FACEBOOK_CLIENT_SECRET')

SITE_DOMAIN = CONFIG.get('deployment', 'SITE_DOMAIN')
API_PORT = CONFIG.getint('deployment', 'API_PORT')
DEPLOY_API = CONFIG.get('deployment', 'DEPLOY_API')

WEB_PORT = CONFIG.getint('deployment', 'WEB_PORT')
DEPLOY_WEB = CONFIG.get('deployment', 'DEPLOY_WEB')
CALLBACK_URL = CONFIG.get('deployment', 'CALLBACK_URL')
LOGIN_URL = CONFIG.get('deployment', 'LOGIN_URL')

SMTP_HOST = CONFIG.get('email', 'SMTP_HOST')
SMTP_PORT = CONFIG.getint('email', 'SMTP_PORT')
SMTP_USER = CONFIG.get('email', 'SMTP_USER')
SMTP_PASSWORD = CONFIG.get('email', 'SMTP_PASSWORD')

SSL_CERT = CONFIG.get('ssl', 'SSL_CERT') if CONFIG.get('ssl', 'SSL_CERT') else None
SSL_KEY = CONFIG.get('ssl', 'SSL_KEY') if CONFIG.get('ssl', 'SSL_KEY') else None
