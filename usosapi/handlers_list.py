from handlers.handlers_api_courses import CourseEditionApi
from handlers.handlers_api_courses import CoursesEditionsApi
from handlers.handlers_api_friends import FriendsSuggestionsApi, FriendsApi
from handlers.handlers_api_grades import GradesForCourseAndTermApi, GradesForUserApi
from handlers.handlers_api_programmes import ProgrammesApi, ProgrammesByIdApi
from handlers.handlers_api_schedule import ScheduleApi
from handlers.handlers_api_terms import TermsApi, TermApi
from handlers.handlers_api_user import UserInfoapi, UsersInfoByIdApi
from handlers.handlers_auth import CreateUserHandler, LoginHandler, LogoutHandler, VerifyHandler
from handlers.handlers_auth import GoogleOAuth2LoginHandler, RegisterHandler
from handlers.handlers_chat import ChatHandler, ChatSocketHandler
from handlers.handlers_web import CourseEdition_WebHandler
from handlers.handlers_web import Courses_WebHandler
from handlers.handlers_web import FriendsHandler
from handlers.handlers_web import FriendsSuggestionsHandler
from handlers.handlers_web import Grades_WebHandler
from handlers.handlers_web import MainHandler, UsersHandler, UserHandlerByUserId
from handlers.handlers_web import ProgrammesWebHandler, Programme_WebHandler
from handlers.handlers_web import ScheduleWebHandler
from handlers.handlers_web import School_Handler
from handlers.handlers_web import SettingsHandler, RegulationsHandler
from handlers.handlers_web import TermsWebHandler, TermWebHandler

HANDLERS = [
    (r"/?", MainHandler),

    (r"/users", UsersHandler),
    (r"/users/([^/]+)", UserHandlerByUserId),

    (r"/school/grades", School_Handler),
    (r"/school/grades/course/([^/]+)/([^/]+)", Grades_WebHandler),
    (r"/school/courses", Courses_WebHandler),
    (r"/school/courseedition/([^/]+)/([^/]+)", CourseEdition_WebHandler),
    (r"/school/terms", TermsWebHandler),
    (r"/school/terms/([^/]+)", TermWebHandler),
    (r"/school/schedule", ScheduleWebHandler),

    (r"/school/programmes", ProgrammesWebHandler),
    (r"/school/programmes/([^/]+)", Programme_WebHandler),

    (r"/chat", ChatHandler),
    (r"/chatsocket", ChatSocketHandler),

    (r"/friends", FriendsHandler),
    (r"/friends/suggestions", FriendsSuggestionsHandler),

    (r"/settings", SettingsHandler),
    (r"/regulations", RegulationsHandler),
    (r"/authentication/register", RegisterHandler),
    (r"/authentication/login", LoginHandler),
    (r"/authentication/logout", LogoutHandler),
    (r"/authentication/create", CreateUserHandler),
    (r"/authentication/verify", VerifyHandler),
    (r"/authentication/google", GoogleOAuth2LoginHandler),

    (r"/api/users/", UserInfoapi),
    (r"/api/users/([^/]+)", UsersInfoByIdApi),

    (r"/api/courseseditions/", CoursesEditionsApi),
    (r"/api/courseedition/([^/]+)/([^/]+)", CourseEditionApi),

    (r"/api/grades/course/([^/]+)/([^/]+)", GradesForCourseAndTermApi),
    (r"/api/grades/", GradesForUserApi),

    (r"/api/terms/", TermsApi),
    (r"/api/terms/([^/]+)", TermApi),

    (r"/api/friends/suggestions/", FriendsSuggestionsApi),

    (r"/api/friends/([^/]+)", FriendsApi),
    (r"/api/friends/", FriendsApi),

    (r"/api/schedule", ScheduleApi),

    (r"/api/programmes/", ProgrammesApi),
    (r"/api/programmes/([^/]+)", ProgrammesByIdApi),

]

