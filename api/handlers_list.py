from handlers import authentication
from handlers.base import UsosesApi, ApplicationConfigHandler
from handlers.courses import CoursesApi, CoursesEditionsApi, CourseEditionApi, CoursesEditionsByTermApi
from handlers.faculties import FacultyByIdApi, FacultiesApi
from handlers.friends import FriendsSuggestionsApi, FriendsApi
from handlers.grades import GradesForCourseAndTermApi, GradesForUserApi, GradesForUserByTermApi
from handlers.lecturers import LecturersApi, LecturerByIdApi
from handlers.programmes import ProgrammesApi, ProgrammesByIdApi
from handlers.terms import TermsApi, TermApi
from handlers.tt import TTApi
from handlers.user import UserInfoApi, UsersInfoByIdApi, UserInfoPhotoApi

HANDLERS = [
    (r"/config", ApplicationConfigHandler),
    (r"/authentication/archive", authentication.ArchiveHandler),
    (r"/authentication/logout", authentication.LogoutHandler),
    (r"/authentication/register", authentication.UsosRegisterHandler),
    (r"/authentication/verify", authentication.UsosVerificationHandler),
    (r"/authentication/google", authentication.GoogleOAuth2LoginHandler),
    (r"/authentication/facebook", authentication.FacebookOAuth2LoginHandler),
    (r"/authentication/mobi", authentication.MobiAuthHandler),
    (r"/authentication/verifymobi", authentication.UsosMobiVerificationHandler),

    (r"/usoses", UsosesApi),

    (r"/users", UserInfoApi),
    (r"/users/([^/]+)", UsersInfoByIdApi),
    (r"/users_info_photos/([^/]+)", UserInfoPhotoApi),

    (r"/courseseditions", CoursesEditionsApi),
    (r"/courseseditionsbyterm", CoursesEditionsByTermApi),
    (r"/courseseditions/([^/]+)/([^/]+)", CourseEditionApi),
    (r"/courses/([^/]+)", CoursesApi),

    (r"/grades/course/([^/]+)/([^/]+)", GradesForCourseAndTermApi),
    (r"/grades", GradesForUserApi),
    (r"/gradesbyterm", GradesForUserByTermApi),

    (r"/terms", TermsApi),
    (r"/terms/([^/]+)", TermApi),

    (r"/friends/suggestions", FriendsSuggestionsApi),
    (r"/friends/([^/]+)", FriendsApi),
    (r"/friends", FriendsApi),

    (r"/lecturers", LecturersApi),
    (r"/lecturers/([^/]+)", LecturerByIdApi),

    (r"/tt/([^/]+)", TTApi),

    (r"/programmes", ProgrammesApi),
    (r"/programmes/([^/]+)", ProgrammesByIdApi),

    (r"/faculties/([^/]+)", FacultyByIdApi),
    (r"/faculties", FacultiesApi),

]

