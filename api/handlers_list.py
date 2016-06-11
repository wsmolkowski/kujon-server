from api.handlers import authentication
from api.handlers.base import UsosesApi, ApplicationConfigHandler
from api.handlers.courses import CoursesApi, CoursesEditionsApi, CourseEditionApi, CoursesEditionsByTermApi
from api.handlers.faculties import FacultyByIdApi, FacultiesApi
from api.handlers.fb_handler import FacebookApi
from api.handlers.friends import FriendsSuggestionsApi, FriendsApi
from api.handlers.grades import GradesForUserApi, GradesForUserByTermApi
from api.handlers.lecturers import LecturersApi, LecturerByIdApi
from api.handlers.programmes import ProgrammesApi, ProgrammesByIdApi
from api.handlers.terms import TermsApi, TermApi
from api.handlers.tt import TTApi
from api.handlers.user import UserInfoApi, UsersInfoByIdApi, UserInfoPhotoApi
from api.handlers.search import SearchUsersApi, SearchCoursesApi, SearchFacultiesApi, SearchProgrammesApi
from api.handlers.theses import ThesesApi

HANDLERS = [
    (r"/config", ApplicationConfigHandler),
    (r"/authentication/archive", authentication.ArchiveHandler),
    (r"/authentication/logout", authentication.LogoutHandler),
    (r"/authentication/register", authentication.UsosRegisterHandler),
    (r"/authentication/verify", authentication.UsosVerificationHandler),
    (r"/authentication/google", authentication.GoogleOAuth2LoginHandler),
    (r"/authentication/facebook", authentication.FacebookOAuth2LoginHandler),

    (r"/usoses", UsosesApi),

    (r"/users", UserInfoApi),
    (r"/users/([^/]+)", UsersInfoByIdApi),
    (r"/users_info_photos/([^/]+)", UserInfoPhotoApi),

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

    (r"/theses", ThesesApi),

]

