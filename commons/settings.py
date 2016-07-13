import os

try:
    from ConfigParser import RawConfigParser  # 2.7
except ImportError:
    from configparser import RawConfigParser  # 3.5

config = RawConfigParser(allow_no_value=True)
DEVELOPMENT = os.environ.get('KUJON_MOBI_DEV')


def parent_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if DEVELOPMENT:
    config.read(os.path.join(parent_dir(), 'config', 'settings-dev.conf'))
else:
    config.read(os.path.join(parent_dir(), 'config', 'settings-prod.conf'))

MONGODB_URI = config.get('database', 'MONGODB_URI')
MONGODB_NAME = config.get('database', 'MONGODB_NAME')

COOKIE_SECRET = config.get('application', 'COOKIE_SECRET')
AES_SECRET = config.get('application', 'AES_SECRET')
ENCRYPT_USOSES_KEYS = config.getboolean('application', 'ENCRYPT_USOSES_KEYS')
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

WEB_VERSION = config.get('deployment', 'WEB_VERSION')
WEB_PORT = config.getint('deployment', 'WEB_PORT')
DEPLOY_WEB = config.get('deployment', 'DEPLOY_WEB')
CALLBACK_URL = config.get('deployment', 'CALLBACK_URL')
CALLBACK_MOBI_URL = config.get('deployment', 'CALLBACK_MOBI_URL')
LOGIN_URL = config.get('deployment', 'LOGIN_URL')

EVENT_PORT = config.getint('deployment', 'EVENT_PORT')
DEPLOY_EVENT = config.get('deployment', 'DEPLOY_EVENT')
LOG_LEVEL = config.get('deployment', 'LOG_LEVEL')

SMTP_HOST = config.get('email', 'SMTP_HOST')
SMTP_PORT = config.getint('email', 'SMTP_PORT')
SMTP_USER = config.get('email', 'SMTP_USER')
SMTP_EMAIL = config.get('email', 'SMTP_EMAIL')
SMTP_PASSWORD = config.get('email', 'SMTP_PASSWORD')

SSL_CERT = config.get('ssl', 'SSL_CERT') if config.get('ssl', 'SSL_CERT') else None
SSL_KEY = config.get('ssl', 'SSL_KEY') if config.get('ssl', 'SSL_KEY') else None

LOG_DIR = config.get('administration', 'LOG_DIR')

APPLICATION_ID = config.get('notification', 'APPLICATION_ID')
AUTHORIZATION = config.get('notification', 'AUTHORIZATION')
