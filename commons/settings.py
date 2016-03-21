MONGODB_URI = "mongodb://localmongoinstance/usos-test2"
MONGODB_NAME = "usos-test2"

COOKIE_SECRET = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
AES_SECRET = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"

PROXY_URL = None
PROXY_PORT = None

GOOGLE_CLIENT_ID = "245488701889-u3n2u20ekptiue8tlaltec5rdhsvanof.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "C8tEnY0XdhEc82Hlx5pBVp9u"

FACEBOOK_CLIENT_ID = "435328606663469"
FACEBOOK_CLIENT_SECRET = "3f2e953dbfebc98a2ea2fc888266f1c4"

PROJECT_TITLE = "Kujon.mobi"

DEBUG = True
RELOAD = False
COMPRESS_RESPONSE = True

SITE_DOMAIN = "localhost"   # important for google and facebook authentication
API_PORT = 8881
DEPLOY_API = "http://{0}:{1}".format(SITE_DOMAIN, API_PORT)

WEB_PORT = 8888
DEPLOY_WEB = "http://{0}:{1}".format(SITE_DOMAIN, WEB_PORT)

CALLBACK_URL = "{0}/authentication/verify".format(API_PORT)

UNICODE = "UTF-8"

LOGIN_URL = "{0}/#login".format(API_PORT)       # here user will be redirected when not logged in attempt for authenticated service

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'smtp_user'
SMTP_PASSWORD = 'smtp_password'