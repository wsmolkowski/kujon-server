from handlers.handlers_api_courses import CourseHandlerApi
from handlers.handlers_api_courses import CoursesEditionsApi
from handlers.handlers_api_friends import FriendsSuggestionsApi, FriendsAddApi, FriendsRemoveApi, FriendsApi
from handlers.handlers_api_grades import GradesForCourseAndTermApi, GradesForUserApi
from handlers.handlers_api_schedule import ScheduleApi
from handlers.handlers_api_terms import TermsApi, TermApi
from handlers.handlers_api_user import UserInfoapi, UsersInfoByIdApi
from handlers.handlers_auth import CreateUserHandler, LoginHandler, LogoutHandler, VerifyHandler, GoogleOAuth2LoginHandler
from handlers.handlers_chat import ChatHandler, ChatSocketHandler
from handlers.handlers_web import CourseInfoWebHandler
from handlers.handlers_web import CoursesWebHandler
from handlers.handlers_web import FriendsHandler
from handlers.handlers_web import FriendsSuggestionsHandler
from handlers.handlers_web import GradesWebHandler
from handlers.handlers_web import MainHandler, UsersHandler, UserHandlerByUserId
from handlers.handlers_web import ScheduleWebHandler
from handlers.handlers_web import SchoolHandler
from handlers.handlers_web import SettingsHandler
from handlers.handlers_web import TermsWebHandler, TermWebHandler

HANDLERS = [
    (r"/?", MainHandler),

    (r"/users", UsersHandler),
    (r"/users/([^/]+)", UserHandlerByUserId),

    (r"/school/grades", SchoolHandler),
    (r"/school/grades/course/([^/]+)/([^/]+)", GradesWebHandler),
    (r"/school/courses", CoursesWebHandler),
    (r"/school/courses/([^/]+)", CourseInfoWebHandler),
    (r"/school/terms", TermsWebHandler),
    (r"/school/terms/([^/]+)", TermWebHandler),
    (r"/school/schedule", ScheduleWebHandler),

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

    (r"/api/users", UserInfoapi),
    (r"/api/users/([^/]+)", UsersInfoByIdApi),
    (r"/api/courseseditions", CoursesEditionsApi),
    (r"/api/courses/([^/]+)", CourseHandlerApi),
    (r"/api/grades/course/([^/]+)/([^/]+)", GradesForCourseAndTermApi),
    (r"/api/grades", GradesForUserApi),
    (r"/api/terms", TermsApi),
    (r"/api/terms/([^/]+)", TermApi),
    (r"/api/friends/suggestions", FriendsSuggestionsApi),
    (r"/api/friends/add/([^/]+)", FriendsAddApi),
    (r"/api/friends/remove/([^/]+)", FriendsRemoveApi),
    (r"/api/friends", FriendsApi),
    (r"/api/schedule", ScheduleApi),


]
