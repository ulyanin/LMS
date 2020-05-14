from typing import List, Tuple
from tornado.web import RequestHandler
from lms.infra.sql_user_factory import SqlUserFactory

from lms.web.handlers import (
    PingHandler,
    NotFoundHandler,
    LoginHandler,
    RegisterHandler,
    GetUserIdHandler,
    GroupHandler,
    UserInfoHandler,
    UserClassmatesHandler,
    UserCoursesHandler,
)

PING_URL = (r'/ping?', PingHandler)
URLS = [
    (r'/login/?', LoginHandler, dict(user_factory=SqlUserFactory)),
    (r'/register/?', RegisterHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/id/?', GetUserIdHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/groups/?', GroupHandler),
    (r'/user/info/?', UserInfoHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/classmates/?', UserClassmatesHandler, dict(user_factory=SqlUserFactory)),
    (r'/user/courses/?', UserCoursesHandler, dict(user_factory=SqlUserFactory)),
    (r"(.*)", NotFoundHandler),
]


def get_all_urls() -> List[Tuple[str, RequestHandler]]:
    return [PING_URL] + URLS
