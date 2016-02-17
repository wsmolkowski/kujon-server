import os

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
PORT = 8881
SSL = False
XSRF_COOKIE = False
LOGIN_URL = "/authentication/login"
STATIC_PATH = os.path.join(ROOT_PATH, 'static')
TEMPLATES_PATH = os.path.join(ROOT_PATH, 'templates')
GZIP = True

# site
SITE_DOMAIN = 'localhost'
SITE_ROOT = '/'

PROJECT_TITLE = "Kujon-web"
PROJECT_DESCRIPTION = ""
DEPLOY_URL = 'http://{0}:{1}'.format(SITE_DOMAIN, PORT)


CLEAN_DB = False

CALLBACK_URL = "http://{0}:{1}/authentication/verify".format(SITE_DOMAIN, PORT)
