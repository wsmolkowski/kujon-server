import os

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
PORT = 8888
XSRF_COOKIE = False
LOGIN_URL = "/authentication/login"
STATIC_PATH = os.path.join(ROOT_PATH, 'static')
TEMPLATES_PATH = os.path.join(ROOT_PATH, 'templates')
GZIP = True

SITE_DOMAIN = 'localhost'
PROJECT_TITLE = "Stara.io"
PROJECT_DESCRIPTION = ""
DEPLOY_URL = 'http://{0}:{1}'.format(SITE_DOMAIN, PORT)

CALLBACK_URL = "http://{0}:{1}/authentication/verify".format(SITE_DOMAIN, PORT)

USOS_API = 'http://localhost:8881'

