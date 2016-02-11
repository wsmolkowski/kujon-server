from handlers.handlers_api_courses import CourseEditionApi
from handlers.handlers_api_courses import CoursesEditionsApi
from handlers.handlers_api_friends import FriendsSuggestionsApi, FriendsApi
from handlers.handlers_api_grades import GradesForCourseAndTermApi, GradesForUserApi
from handlers.handlers_api_lecturers import LecturersApi, LecturerByIdApi
from handlers.handlers_api_programmes import ProgrammesApi, ProgrammesByIdApi
from handlers.handlers_api_schedule import ScheduleApi
from handlers.handlers_api_terms import TermsApi, TermApi
from handlers.handlers_api_user import UserInfoapi, UsersInfoByIdApi
from handlers.handlers_auth import CreateUserHandler, LoginHandler, LogoutHandler, VerifyHandler
from handlers.handlers_auth import GoogleOAuth2LoginHandler, RegisterHandler
from handlers.handlers_chat import ChatHandler, ChatSocketHandler
from handlers.handlers_web import CourseEdition_WebHandler
from handlers.handlers_web import Courses_WebHandler
from handlers.handlers_web import FriendsSuggestions_WebHandler
from handlers.handlers_web import Friends_WebHandler
from handlers.handlers_web import Grades_WebHandler
from handlers.handlers_web import Lecturers_WebHandler, Lecturer_WebHandler
from handlers.handlers_web import Main_WebHandler, Users_WebHandler, UserByUserId_WebHandler
from handlers.handlers_web import Programmes_WebHandler, Programme_WebHandler
from handlers.handlers_web import Schedule_WebHandler
from handlers.handlers_web import School_WebHandler
from handlers.handlers_web import Settings_WebHandler, Regulations_WebHandler
from handlers.handlers_web import Terms_WebHandler, Term_WebHandler

HANDLERS = [
    (r"/?", Main_WebHandler),

    (r"/users", Users_WebHandler),
    (r"/users/([^/]+)", UserByUserId_WebHandler),

    (r"/school/grades", School_WebHandler),
    (r"/school/grades/course/([^/]+)/([^/]+)", Grades_WebHandler),
    (r"/school/courses", Courses_WebHandler),
    (r"/school/courseedition/([^/]+)/([^/]+)", CourseEdition_WebHandler),
    (r"/school/terms", Terms_WebHandler),
    (r"/school/terms/([^/]+)", Term_WebHandler),
    (r"/school/schedule", Schedule_WebHandler),

    (r"/school/programmes", Programmes_WebHandler),
    (r"/school/programmes/([^/]+)", Programme_WebHandler),

    (r"/school/lecturers", Lecturers_WebHandler),
    (r"/school/lecturers/([^/]+)", Lecturer_WebHandler),

    (r"/chat", ChatHandler),
    (r"/chatsocket", ChatSocketHandler),

    (r"/friends", Friends_WebHandler),
    (r"/friends/suggestions", FriendsSuggestions_WebHandler),

    (r"/settings", Settings_WebHandler),
    (r"/regulations", Regulations_WebHandler),
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

    (r"/api/lecturers/", LecturersApi),
    (r"/api/lecturers/([^/]+)", LecturerByIdApi),

    (r"/api/schedule", ScheduleApi),

    (r"/api/programmes/", ProgrammesApi),
    (r"/api/programmes/([^/]+)", ProgrammesByIdApi),

]

