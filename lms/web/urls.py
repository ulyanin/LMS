from typing import List, Tuple
from tornado.web import RequestHandler
from lms.infra.sql_user_factory import SqlUserFactory
from lms.infra.sql_course import SqlCourse
from lms.settings import COOKIE_SECRET

from lms.web.handlers import (
    PingHandler,
    NotFoundHandler,
    LoginHandler,
    RegisterHandler,
    ChangePasswordHandler,
    GetUserIdHandler,
    UserInfoHandler,
    UserClassmatesHandler,
    UserCoursesHandler,
    CourseInfoHandler,
    AssigneesViewerHandler,
    AssigneeSubmitHandler,
)

PING_URL = (r'/ping?', PingHandler)
URLS = [
    (r'/login/?', LoginHandler, dict(user_factory=SqlUserFactory)),
    (r'/register/?', RegisterHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/change_password/?', ChangePasswordHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/id/?', GetUserIdHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/info/?', UserInfoHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/classmates/?', UserClassmatesHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/courses/?', UserCoursesHandler, dict(user_factory=SqlUserFactory)),
    (
        r'/course/info/?',
        CourseInfoHandler,
        dict(user_factory=SqlUserFactory, course_class=SqlCourse)
    ),
    (
        r'/assignee/view/?',
        AssigneesViewerHandler,
        dict(user_factory=SqlUserFactory, course_class=SqlCourse)
    ),
    (
        r'/assignee/submit/?',
        AssigneeSubmitHandler,
        dict(user_factory=SqlUserFactory, course_class=SqlCourse)
    ),
    (r"(.*)", NotFoundHandler),
]
LOGIN_URL = [
    '/login',
]
SETTINGS = {
    'cookie_secret': COOKIE_SECRET,
    'login_url': '/login',
}


def get_all_urls() -> List[Tuple[str, RequestHandler]]:
    return [PING_URL] + URLS


def get_settings():
    return SETTINGS
