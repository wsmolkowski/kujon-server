# coding=UTF-8
ENCODING = "UTF-8"

MONGO_ID = "_id"
ID = "id"
USOS_ID = "usos_id"
USER_ID = "user_id"
MOBILE_ID = "mobile_id"
COURSE_ID = "course_id"
TERM_ID = "term_id"
UNIT_ID = "unit_id"
GROUP_ID = "course_unit_id"
FRIEND_ID = "friend_id"
PROGRAMME_ID = "programme_id"
FACULTY_ID = "fac_id"
TT_STARTDATE = "start_date"

PARTICIPANTS = "participants"
LECTURERS = "lecturers"

CREATED_TIME = "created_time"
UPDATE_TIME = "update_time"
ACCESS_TOKEN_KEY = "access_token_key"
ACCESS_TOKEN_SECRET = "access_token_secret"
OAUTH_VERIFIER = "oauth_verifier"

USOS_URL = "url"
CONSUMER_KEY = "consumer_key"
CONSUMER_SECRET = "consumer_secret"

JOB_STATUS = "status"
JOB_TYPE = "type"
JOB_PENDING = "pending"
JOB_START = "start"
JOB_FINISH = "finish"
JOB_FAIL = "fail"
JOB_MESSAGE = "message"

USER_TYPE = "user_type"
USER_CREATED = "user_created"
USOS_PAIRED = "usos_paired"
USER_NAME = "name"
USER_EMAIL = "email"
USER_PICTURE = "picture"

USER_PRESENT_KEYS = (MOBILE_ID, USOS_ID, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
KUJON_SECURE_COOKIE = "KUJON_SECURE_COOKIE"
KUJON_CONFIG_COOKIE = "KUJON_CONFIG_COOKIE"

COOKIE_EXPIRES_DAYS = 10
OAUTH_TOKEN = "oauth_token"
OAUTH_TOKEN_SECRET = "oauth_token_secret"

LECTURER_STATUS = "staff_status"
LECTURER_STATUS_ACTIVE = 2

ALERT_MESSAGE = "alert_message"
GRADE_FINAL = "Końcowa"

COLLECTION_USERS = "users"
COLLECTION_USERS_ARCHIVE = "users_archive"
COLLECTION_USOSINSTANCES = "usosinstances"
COLLECTION_COURSES_CLASSTYPES = "courses_classtypes"
COLLECTION_COURSES_UNITS = "courses_units"
COLLECTION_COURSES = "courses"
COLLECTION_USERS_INFO = "users_info"
COLLECTION_COURSES_EDITIONS = "courses_editions"
COLLECTION_TERMS = "terms"
COLLECTION_COURSE_EDITION = "course_edition"
COLLECTION_GRADES = "grades"
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

DATETIME_DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"
CRAWL_USER_UPDATE = 120   #   minutes after crawler updates user data
CRAWL_TYPE = "crawl_type"

SMTP_SUBJECT = 'subject'
SMTP_FROM = 'from'
SMTP_TO = 'to'
SMTP_TEXT = 'text'
SMTP_MIME_TYPE = 'mime_type'
SMTP_CHARSET = 'charset'
