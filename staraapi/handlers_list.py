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
from handlers.handlers_api_user import UserInfoApi, UsersInfoByIdApi, UserInfoPhotoApi

HANDLERS = [

    (r"/api/usoses", UsosesApi),
    (r"/api/users/", UserInfoApi),
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

