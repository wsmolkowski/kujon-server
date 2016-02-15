from handlers.handlers_api import UsosesApi
from handlers.handlers_api_courses import CoursesApi
from handlers.handlers_api_courses import CoursesEditionsApi
from handlers.handlers_api_faculties import FacultyByIdApi
from handlers.handlers_api_friends import FriendsSuggestionsApi, FriendsApi
from handlers.handlers_api_grades import GradesForCourseAndTermApi, GradesForUserApi
from handlers.handlers_api_lecturers import LecturersApi, LecturerByIdApi
from handlers.handlers_api_programmes import ProgrammesApi, ProgrammesByIdApi
from handlers.handlers_api_schedule import ScheduleApi
from handlers.handlers_api_terms import TermsApi, TermApi
from handlers.handlers_api_user import UserInfoapi, UsersInfoByIdApi, UserInfoPhotoApi
from handlers.handlers_auth import CreateUserHandler, LoginHandler, LogoutHandler, VerifyHandler
from handlers.handlers_auth import GoogleOAuth2LoginHandler, RegisterHandler
from handlers.handlers_chat import ChatHandler, ChatSocketHandler
from handlers.handlers_web import CourseWebHandler
from handlers.handlers_web import CoursesWebHandler
from handlers.handlers_web import FriendsSuggestionsWebHandler
from handlers.handlers_web import FriendsWebHandler
from handlers.handlers_web import GradesWebHandler
from handlers.handlers_web import LecturersWebHandler, LecturerWebHandler
from handlers.handlers_web import MainWebHandler, UsersWebHandler, UserByUserIdWebHandler
from handlers.handlers_web import ProgrammesWebHandler, ProgrammeWebHandler
from handlers.handlers_web import ScheduleWebHandler
from handlers.handlers_web import SchoolWebHandler
from handlers.handlers_web import SettingsWebHandler, RegulationsWebHandler
from handlers.handlers_web import TermsWebHandler, TermWebHandler

HANDLERS = [
    (r"/?", MainWebHandler),

    (r"/users", UsersWebHandler),
    (r"/users/([^/]+)", UserByUserIdWebHandler),

    (r"/school/grades", SchoolWebHandler),
    (r"/school/grades/course/([^/]+)/([^/]+)", GradesWebHandler),
    (r"/school/courses", CoursesWebHandler),
    (r"/school/courses/([^/]+)", CourseWebHandler),
    (r"/school/terms", TermsWebHandler),
    (r"/school/terms/([^/]+)", TermWebHandler),
    (r"/school/schedule", ScheduleWebHandler),

    (r"/school/programmes", ProgrammesWebHandler),
    (r"/school/programmes/([^/]+)", ProgrammeWebHandler),

    (r"/school/lecturers", LecturersWebHandler),
    (r"/school/lecturers/([^/]+)", LecturerWebHandler),

    (r"/chat", ChatHandler),
    (r"/chatsocket", ChatSocketHandler),

    (r"/friends", FriendsWebHandler),
    (r"/friends/suggestions", FriendsSuggestionsWebHandler),

    (r"/settings", SettingsWebHandler),
    (r"/regulations", RegulationsWebHandler),
    (r"/authentication/register", RegisterHandler),
    (r"/authentication/login", LoginHandler),
    (r"/authentication/logout", LogoutHandler),
    (r"/authentication/create", CreateUserHandler),
    (r"/authentication/verify", VerifyHandler),
    (r"/authentication/google", GoogleOAuth2LoginHandler),

    (r"/api/usoses", UsosesApi),
    (r"/api/users/", UserInfoapi),
    (r"/api/users/([^/]+)", UsersInfoByIdApi),
    (r"/api/users_info_photos/([^/]+)", UserInfoPhotoApi),

    (r"/api/courseseditions/", CoursesEditionsApi),
    (r"/api/courses/([^/]+)", CoursesApi),

    (r"/api/grades/course/([^/]+)/([^/]+)", GradesForCourseAndTermApi),
    (r"/api/grades/", GradesForUserApi),

    (r"/api/terms/", TermsApi),
    (r"/api/terms/([^/]+)", TermApi),

    (r"/api/friends/suggestions/", FriendsSuggestionsApi),

    (r"/api/friends/([^/]+)", FriendsApi),
    (r"/api/friends/", FriendsApi),

    (r"/api/lecturers/", LecturersApi),
    (r"/api/lecturers/([^/]+)", LecturerByIdApi),

    (r"/api/schedule", ScheduleApi),

    (r"/api/programmes/", ProgrammesApi),
    (r"/api/programmes/([^/]+)", ProgrammesByIdApi),

    (r"/api/faculties/([^/]+)", FacultyByIdApi),

]

