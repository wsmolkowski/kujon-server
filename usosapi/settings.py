import os

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
PORT = 8888
SSL = False
XSRF_COOKIE = False
COOKIE_SECRET = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
LOGIN_URL = "/authentication/login"
STATIC_PATH = os.path.join(ROOT_PATH, 'static')
TEMPLATES_PATH = os.path.join(ROOT_PATH, 'templates')
#AUTORELOAD_ENABLED = False
GZIP = True

# site
SITE_DOMAIN = 'localhost'
SITE_ROOT = '/'

PROJECT_TITLE = "Kujon-web"
PROJECT_DESCRIPTION = ""
DEPLOY_URL = 'http://{0}:{1}'.format(SITE_DOMAIN, PORT)

MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'usos-test2'

CLEAN_DB = False

CALLBACK_URL = "http://{0}:{1}/authentication/verify".format(SITE_DOMAIN, PORT)
PROXY_URL = None    #
PROXY_PORT = None   #

GOOGLE_CLIENT_ID = "245488701889-dfhvfuf9br6u6t9476gt0l5ngkvacota.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "Pl3jCVQO55nZMhxKXHNWivZp"

