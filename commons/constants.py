# coding=UTF-8
ENCODING = "UTF-8"

MONGO_ID = "_id"
ID = "id"
USOS_ID = "usos_id"
USER_ID = "user_id"
MOBILE_ID = "mobile_id"
COURSE_ID = "course_id"
COURSE_NAME = "course_name"
TERM_ID = "term_id"
TERMS_ORDER_KEY = "order_key"
UNIT_ID = "unit_id"
GROUP_ID = "course_unit_id"
FRIEND_ID = "friend_id"
PROGRAMME_ID = "programme_id"
FACULTY_ID = "fac_id"
FACULTY_NAME = "name"
TT_STARTDATE = "start_date"
COURSE_EDITIONS = "course_editions"
CLASS_TYPE = "class_type"
CLASS_TYPE_ID = "classtype_id"
VALUE_DESCRIPTION = "value_description"
PHOTO_URL = "photo_url"
PARTICIPANTS = "participants"
LECTURERS = "lecturers"
COORDINATORS = "coordinators"
PICTURE = 'picture'
GRADES = 'grades'
SEARCH_QUERY = 'query'
SEARCH_ENDPOINT = 'endpoint'
NODE_ID = 'node_id'
USOS_USER_ID = 'usos_user_id'

FACEBOOK = "facebook"
FACEBOOK_ID = "id"
FACEBOOK_NAME = "name"
FACEBOOK_EMAIL = "email"
FACEBOOK_ACCESS_TOKEN = "access_token"
FACEBOOK_SESSION_EXPIRES = "session_expires"
FACEBOOK_PICTURE = "picture"

FIELD_TOKEN_EXPIRATION = 'exp'
TOKEN_EXPIRATION_TIMEOUT = 3600

GOOGLE = 'google'
GOOGLE_NAME = 'name'
GOOGLE_EMAIL = 'email'
GOOGLE_PICTURE = 'picture'
GOOGLE_ACCESS_TOKEN = 'access_token'
GOOGLE_EXPIRES_IN = 'expires_in'
GOOGLE_ID_TOKEN = 'id_token'
GOOGLE_TOKEN_TYPE = 'token_type'

CREATED_TIME = "created_time"
UPDATE_TIME = "update_time"
ACCESS_TOKEN_KEY = "access_token_key"
ACCESS_TOKEN_SECRET = "access_token_secret"
OAUTH_VERIFIER = "oauth_verifier"

USOS_URL = "url"
USOS_NAME = "name"
USOS_LOGO = "logo"
CONSUMER_KEY = "consumer_key"
CONSUMER_SECRET = "consumer_secret"

JOB_STATUS = "status"
JOB_TYPE = "type"
JOB_MESSAGE = "message"
JOB_DATA = "job_data"

USER_TYPE = "user_type"
USER_CREATED = "user_created"
USOS_PAIRED = "usos_paired"
USER_NAME = "name"
USER_EMAIL = "email"
USER_PICTURE = "picture"

USER_PRESENT_KEYS = (MOBILE_ID, USOS_ID, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

MOBI_TOKEN = "mobi_token"

LECTURER_STATUS = "staff_status"
LECTURER_STATUS_ACTIVE = 2

ALERT_MESSAGE = "alert_message"
GRADE_FINAL = "Końcowa"

FIELD_MESSAGE_FROM = 'from'
FIELD_MESSAGE_TYPE = 'typ'
FIELD_MESSAGE_TEXT = 'text'

COLLECTION_USERS = "users"
COLLECTION_USERS_ARCHIVE = "users_arch"
COLLECTION_USOSINSTANCES = "usosinstances"
COLLECTION_COURSES_CLASSTYPES = "courses_classtypes"
COLLECTION_COURSES_UNITS = "courses_units"
COLLECTION_COURSES = "courses"
COLLECTION_USERS_INFO = "users_info"
COLLECTION_COURSES_EDITIONS = "courses_editions"
COLLECTION_TERMS = "terms"
COLLECTION_FRIENDS = "friends"
COLLECTION_PROGRAMMES = "programmes"
COLLECTION_GROUPS = "groups"
COLLECTION_PHOTOS = "users_info_photos"
COLLECTION_FACULTIES = "faculties"
COLLECTION_TT = "tts"
COLLECTION_JOBS_QUEUE = "jobs_queue"
COLLECTION_JOBS_LOG = "jobs_queue_log"
COLLECTION_STATISTICS_HISTORY = 'statistic_history'
COLLECTION_EMAIL_QUEUE = 'email_queue'
COLLECTION_EMAIL_QUEUE_LOG = 'email_queue_log'
COLLECTION_EXCEPTIONS = 'exceptions'
COLLECTION_TOKENS = 'tokens'
COLLECTION_SUBSCRIPTIONS = 'subscriptions'
COLLECTION_MESSAGES = 'messages'
COLLECTION_NOTIFIER_STATUS = 'notifier_status'
COLLECTION_NOTIFICATION_QUEUE = 'notification_queue'
COLLECTION_NOTIFICATION_QUEUE_LOG = 'notification_queue_log'
COLLECTION_SEARCH = 'search'
COLLECTION_THESES = 'theses'
COLLECTION_CRSTESTS = 'crstests'
COLLECTION_CRSTESTS_GRADES = 'crstests_grades'
COLLECTION_CRSTESTS_POINTS = 'crstests_points'

COOKIE_FIELDS = (ID, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, USOS_ID, USOS_PAIRED, USER_EMAIL, USER_NAME, USER_PICTURE,
                 GOOGLE, FACEBOOK, USOS_USER_ID)

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

MOBILE_X_HEADER_EMAIL = 'X-Kujonmobiemail'
MOBILE_X_HEADER_TOKEN = 'X-Kujonmobitoken'
MOBILE_X_HEADER_REFRESH = 'X-Kujonrefresh'
EVENT_X_HUB_SIGNATURE = 'X-Hub-Signature'

SECONDS_1MONTH = 2592000
SECONDS_2MONTHS = 5184000
SECONDS_DAY = 86400
SECONDS_1WEEK = 604800
SECONDS_2WEEKS = 1209600
SECONDS_HOUR = 3600

MAX_HTTP_CLIENTS = 1000

HTTP_CONNECT_TIMEOUT = 50
HTTP_REQUEST_TIMEOUT = 50
HTTP_VALIDATE_CERT = True
