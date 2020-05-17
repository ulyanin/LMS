# pylint: disable=abstract-method
# pylint: disable=arguments-differ
# pylint: disable=attribute-defined-outside-init

import json
from typing import Optional, Any

import tornado.escape
import tornado.web

from tornado.web import (
    RequestHandler,
    authenticated,
)


class PingHandler(RequestHandler):
    _response = {
        'status': 'ok',
    }

    def get(self):
        self.write(self._response)
        self.set_status(200)
        self.finish()


class BaseHandler(RequestHandler):
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.finish({
            'code': status_code,
            'msg': self._reason,
        })


class NotFoundHandler(BaseHandler):
    def prepare(self):
        raise tornado.web.HTTPError(
            status_code=404,
            reason="Invalid resource path."
        )


class UserHandler(BaseHandler):
    def initialize(self, user_factory):
        self.user_factory = user_factory
        self.body = dict()
        self.msg = None
        if self.request.body:
            try:
                self.body = tornado.escape.json_decode(self.request.body)
            except json.decoder.JSONDecodeError as exception:
                self.msg = f'could not parse body:\n{str(exception)}'

    async def prepare(self):  # pylint: disable=invalid-overridden-method
        if self.msg:
            self._bad_request(
                status=400,
                msg=self.msg,
            )

    def get_current_user(self) -> Optional[bytes]:
        return self.get_secure_cookie('user_id')

    def get_current_user_id(self) -> Optional[int]:
        user_id = self.get_current_user()
        if user_id:
            return int(user_id)
        return None

    def _bad_request(self, status=400, *, msg):
        self.set_status(status)
        self.write({
            'status': 'err',
            'msg': msg
        })
        self.finish()


class GetUserIdHandler(UserHandler):
    def get(self):
        user_id = self.get_current_user()
        if user_id:
            user_id = user_id.decode('utf-8')
        self.write({
            'user_id': user_id
        })


class LoginHandler(UserHandler):
    def initialize(self, user_factory):
        super().initialize(user_factory=user_factory)
        self.email = self.body.get('email')
        self.password = self.body.get('password')

    def get(self):
        self.write({
            'status': 'err',
            'msg': 'user POST to login'
        })
        self.finish()

    async def post(self):
        user_id = await self.user_factory.login_user(email=self.email, password=self.password)
        if user_id:
            self.set_secure_cookie("user_id", str(user_id))
            self.write({
                'status': 'ok',
                'msg': 'successfully logged in, set cookies in header',
            })
        else:
            self._bad_request(status=401, msg='incorrect email or password or user has not been registered')


class RegisterHandler(UserHandler):
    def initialize(self, user_factory):
        super().initialize(user_factory=user_factory)
        self.verification_code = self.body.get('verification_code')
        self.email = self.body.get('email')
        self.password = self.body.get('password')

    async def post(self):
        success, msg = await self.user_factory.register_user(
            verification_code=self.verification_code,
            email=self.email,
            password=self.password
        )
        if not success:
            self._bad_request(status=401, msg=msg)
        else:
            self.write({
                'status': 'ok',
                'msg': msg,
            })


class AuthUserHandler(UserHandler):
    def initialize(self, user_factory):
        super().initialize(user_factory=user_factory)

    async def prepare(self):
        await super().prepare()
        self.user_id = self.get_current_user_id()
        if self.user_id is None:
            raise tornado.web.HTTPError(403)
        self.user = await self.user_factory.get_student_or_professor(
            user_id=self.user_id
        )


class UserInfoHandler(UserHandler):
    def initialize(self, user_factory):
        super().initialize(user_factory)
        self.user_id = self.get_current_user_id()
        self.authenticated = self.user_id is not None
        if self.get_argument('user_id', default=None):
            self.user_id = self.get_argument('user_id')
            if self.user_id:
                self.user_id = int(self.user_id)
            self.authenticated &= self.user_id == self.get_current_user_id()

    async def prepare(self):
        await super().prepare()
        if self.user_id is not None:
            self.user = await self.user_factory.get_student_or_professor(
                user_id=self.user_id,
                authenticated=self.authenticated
            )

    def _doesnt_exist(self):
        self._bad_request(
            status=400,
            msg=f"user_id {self.user_id} does not exist"
        )

    async def get(self):
        if not self.user_id:
            self._bad_request(msg='expected authentication or user_id within GET argument')
            assert False
        info = await self.user.get_info()
        if not info:
            self._doesnt_exist()
            return
        self.write({
            'status': 'ok',
            'info': info,
        })

    @authenticated
    async def post(self):
        if self.user_id != self.get_current_user_id():
            self._bad_request(
                msg='could not perform update for other user, please verify user_id GET argument'
            )
            return
        to_update = self.body.get('update')
        if to_update is None:
            self._bad_request(
                msg='expected "update" property in body; POST request is used to modify user_info'
            )
            return
        update_result = await self.user.update_info(update=to_update)
        if update_result.success:
            self.write({
                'status': 'ok',
                'updated': True,
                'msg': f'successfully update info for user_id = {self.user_id}',
            })
        else:
            self.write({
                'status': 'err',
                'updated': False,
                'msg': update_result.msg,
            })


class UserClassmatesHandler(AuthUserHandler):
    _CLASSMATE_FIELDS = ('user_id', 'name')

    async def prepare(self):
        await super().prepare()
        if await self.user.is_professor:
            self._bad_request(status=405, msg='method classmates is not allowed for professor')
            return
        self.classmates = await self.user.classmates()

    async def get(self):
        classmates = []
        for classmate in self.classmates:
            classmates.append(
                await classmate.get_info(properties=self._CLASSMATE_FIELDS)
            )
        self.write({
            'status': 'ok',
            'classmates': classmates,
        })


class UserCoursesHandler(AuthUserHandler):
    _COURSES_FIELDS = ('course_id', 'name')

    async def prepare(self):
        await super().prepare()
        self.courses = await self.user.courses()

    async def get(self):
        courses = [
            await course.get_info(properties=self._COURSES_FIELDS)
            for course in self.courses
        ]
        self.write({
            'status': 'ok',
            'courses': courses,
        })


class EditUserInfoHandler(AuthUserHandler):
    def initialize(self, user_factory):
        super().initialize(user_factory)
        self.update = self.body.get('update')

    async def prepare(self):
        await super().prepare()
        if not self.update:
            self._bad_request(msg='expected "update" parameter')
        for param in self.update:
            if param not in self.user.EDITABLE_PARAMS:
                self._bad_request(
                    msg=f'unexpected field {param} does not exist or cannot be updated'
                )


class BaseCourseHandler(AuthUserHandler):
    def initialize(self, user_factory, course_class):
        super().initialize(user_factory)
        course_id = self.get_argument('course_id', default=None)
        if course_id:
            course_id = int(course_id)
        self.course = course_class(course_id=course_id)

    async def prepare(self):
        await super().prepare()
        if not self.course:
            self._bad_request(
                msg='expected course_id GET parameter'
            )
            return


class CourseInfoHandler(BaseCourseHandler):
    async def get(self):
        info = await self.course.get_info()
        self.write({
            'status': 'ok',
            'info': info,
        })
