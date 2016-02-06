from handlers.handlers_api_courses import CourseHandlerApi
from handlers.handlers_api_courses import CoursesEditionsApi
from handlers.handlers_api_friends import FriendsSuggestionsApi, FriendsAddApi
from handlers.handlers_api_grades import GradesForCourseAndTermApi, GradesForUserApi
from handlers.handlers_api_terms import TermsApi, TermApi
from handlers.handlers_api_user import UserApi
from handlers.handlers_auth import CreateUserHandler, LoginHandler, LogoutHandler, VerifyHandler, GoogleOAuth2LoginHandler
from handlers.handlers_chat import ChatHandler, ChatSocketHandler
from handlers.handlers_web import CourseInfoWebHandler
from handlers.handlers_web import CoursesWebHandler
from handlers.handlers_web import FriendsHandler
from handlers.handlers_web import FriendsSuggestionsHandler
from handlers.handlers_web import GradesWebHandler
from handlers.handlers_web import MainHandler, UserHandler
from handlers.handlers_web import SchoolHandler
from handlers.handlers_web import SettingsHandler
from handlers.handlers_web import TermsWebHandler, TermWebHandler

HANDLERS = [
    (r"/?", MainHandler),

    (r"/user", UserHandler),

    (r"/school", SchoolHandler),
    (r"/school/grades", SchoolHandler),
    (r"/school/grades/course/([^/]+)/([^/]+)", GradesWebHandler),
    (r"/school/courses", CoursesWebHandler),
    (r"/school/courses/([^/]+)", CourseInfoWebHandler),
    (r"/school/terms", TermsWebHandler),
    (r"/school/terms/([^/]+)", TermWebHandler),

    (r"/chat", ChatHandler),
    (r"/chatsocket", ChatSocketHandler),

    (r"/friends", FriendsHandler),
    (r"/friends/suggestions", FriendsSuggestionsHandler),

    (r"/settings", SettingsHandler),

    (r"/authentication/login", LoginHandler),
    (r"/authentication/logout", LogoutHandler),
    (r"/authentication/create", CreateUserHandler),
    (r"/authentication/verify", VerifyHandler),
    (r"/authentication/google", GoogleOAuth2LoginHandler),

    (r"/api/user", UserApi),

    (r"/api/courseseditions", CoursesEditionsApi),
    (r"/api/courses/([^/]+)", CourseHandlerApi),

    (r"/api/grades/course/([^/]+)/([^/]+)", GradesForCourseAndTermApi),
    (r"/api/grades", GradesForUserApi),

    (r"/api/terms", TermsApi),
    (r"/api/terms/([^/]+)", TermApi),

    (r"/api/friends/suggestions", FriendsSuggestionsApi),
    (r"/api/friends/add/([^/]+)/([^/]+)", FriendsAddApi),


]
