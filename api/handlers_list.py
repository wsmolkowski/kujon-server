# coding=utf-8

from api.handlers import authentication
from api.handlers import settings
from api.handlers.base import UsosesApi, UsosesAllApi, ApplicationConfigHandler
from api.handlers.courses import CoursesApi, CoursesEditionsApi, CourseEditionApi, CoursesEditionsByTermApi
from api.handlers.crstests import CrsTestsApi, CrsTestsNodeApi
from api.handlers.faculties import FacultyByIdApi, FacultiesApi
from api.handlers.fb_handler import FacebookApi
from api.handlers.files import FilesHandler, FileHandler
from api.handlers.friends import FriendsSuggestionsApi, FriendsApi
from api.handlers.grades import GradesForUserApi, GradesForUserByTermApi
from api.handlers.lecturers import LecturersApi, LecturerByIdApi
from api.handlers.messages import MessagesHandler
from api.handlers.programmes import ProgrammesApi, ProgrammesByIdApi
from api.handlers.search import SearchUsersApi, SearchCoursesApi, SearchFacultiesApi, SearchProgrammesApi, \
    SearchThesesApi
from api.handlers.subscriptions import SubscriptionsHandler
from api.handlers.terms import TermsApi, TermApi
from api.handlers.theses import ThesesApi
from api.handlers.tt import TTApi
from api.handlers.user import UsersInfoApi, UsersInfoAllApi, UsersInfoByIdApi, UsersInfoPhotoApi

HANDLERS = [
    (r"/config", ApplicationConfigHandler),
    (r"/authentication/archive", authentication.ArchiveHandler),
    (r"/authentication/logout", authentication.LogoutHandler),
    (r"/authentication/register", authentication.UsosRegisterHandler),
    (r"/authentication/verify", authentication.UsosVerificationHandler),
    (r"/authentication/google", authentication.GoogleOAuth2LoginHandler),
    (r"/authentication/facebook", authentication.FacebookOAuth2LoginHandler),

    (r"/authentication/email_register", authentication.EmailRegisterHandler),
    (r"/authentication/email_login", authentication.EmailLoginHandler),
    (r"/authentication/email_confim/([^/]+)", authentication.EmailConfirmHandler),

    (r"/settings", settings.SettingsHandler),
    (r"/settings/event/enable", settings.EventEnableHandler),
    (r"/settings/event/disable", settings.EventDisableHandler),
    (r"/settings/googlecalendar/enable", settings.GoogleCallendarEnableHandler),
    (r"/settings/googlecalendar/disable", settings.GoogleCallendarDisableHandler),

    (r"/usoses", UsosesApi),
    (r"/usosesall", UsosesAllApi),

    (r"/usersinfoall", UsersInfoAllApi),
    (r"/users", UsersInfoApi),
    (r"/users/([^/]+)", UsersInfoByIdApi),
    (r"/users_info_photos/([^/]+)", UsersInfoPhotoApi),

    (r"/courseseditions", CoursesEditionsApi),
    (r"/courseseditionsbyterm", CoursesEditionsByTermApi),
    (r"/courseseditions/([^/]+)/([^/]+)", CourseEditionApi),
    (r"/courses/([^/]+)", CoursesApi),

    (r"/grades", GradesForUserApi),
    (r"/gradesbyterm", GradesForUserByTermApi),

    (r"/terms", TermsApi),
    (r"/terms/([^/]+)", TermApi),

    (r"/friends/suggestions", FriendsSuggestionsApi),
    (r"/friends/([^/]+)", FriendsApi),
    (r"/friends", FriendsApi),
    (r"/facebook", FacebookApi),

    (r"/lecturers", LecturersApi),
    (r"/lecturers/([^/]+)", LecturerByIdApi),

    (r"/tt/([^/]+)", TTApi),

    (r"/programmes", ProgrammesApi),
    (r"/programmes/([^/]+)", ProgrammesByIdApi),

    (r"/faculties/([^/]+)", FacultyByIdApi),
    (r"/faculties", FacultiesApi),

    (r"/search/users/([^/]+)", SearchUsersApi),
    (r"/search/courses/([^/]+)", SearchCoursesApi),
    (r"/search/faculties/([^/]+)", SearchFacultiesApi),
    (r"/search/programmes/([^/]+)", SearchProgrammesApi),
    (r"/search/theses/([^/]+)", SearchThesesApi),

    (r"/theses", ThesesApi),

    (r"/crstests", CrsTestsApi),
    (r"/crstests/([^/]+)", CrsTestsNodeApi),

    (r"/subscriptions", SubscriptionsHandler),

    (r"/messages", MessagesHandler),

    (r"/files", FilesHandler),
    (r"/files/([^/]+)", FileHandler),
]
