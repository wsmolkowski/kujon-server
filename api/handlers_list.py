from handlers.base import UsosesApi
from handlers.courses import CoursesApi, CoursesEditionsApi, CourseEditionApi
from handlers.faculties import FacultyByIdApi
from handlers.friends import FriendsSuggestionsApi, FriendsApi
from handlers.grades import GradesForCourseAndTermApi, GradesForUserApi
from handlers.lecturers import LecturersApi, LecturerByIdApi
from handlers.programmes import ProgrammesApi, ProgrammesByIdApi
from handlers.tt import TTApi
from handlers.terms import TermsApi, TermApi
from handlers.user import UserInfoApi, UsersInfoByIdApi, UserInfoPhotoApi

HANDLERS = [
    (r"/api/usoses", UsosesApi),

    (r"/api/users/", UserInfoApi),
    (r"/api/users/([^/]+)", UsersInfoByIdApi),
    (r"/api/users_info_photos/([^/]+)", UserInfoPhotoApi),

    (r"/api/courseseditions/", CoursesEditionsApi),
    (r"/api/courseseditions/([^/]+)/([^/]+)", CourseEditionApi),
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

    (r"/api/tt/([^/]+)", TTApi),

    (r"/api/programmes/", ProgrammesApi),
    (r"/api/programmes/([^/]+)", ProgrammesByIdApi),

    (r"/api/faculties/([^/]+)", FacultyByIdApi),

]

