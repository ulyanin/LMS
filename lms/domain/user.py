# pylint: disable=too-few-public-methods

from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable, List, Optional


class UpdateResult:
    def __init__(self, *, success: bool, msg=None):
        self.success = success
        self.msg = msg


class User(metaclass=ABCMeta):
    USER_PROPERTIES = (
        'user_id',
        'role',
        'name',
        'email',
        'telephone',
        'city',
        'info',
        'vk_link',
        'instagram_link',
        'fb_link',
        'linkedin_link',
    )
    EDITABLE_USER_PROPERTIES = (
        'telephone',
        'city',
        'info',
        'vk_link',
        'instagram_link',
        'fb_link',
        'linkedin_link',
    )

    def __init__(self, *, user_id, authenticated=False):
        self.user_id = user_id
        self.authenticated = authenticated

    def properties(self):
        return self.USER_PROPERTIES

    def editable_properties(self):
        return self.EDITABLE_USER_PROPERTIES

    @staticmethod
    def hidden_properties():
        return tuple()

    @abstractmethod
    async def get_info(
            self,
            *,
            properties: Optional[Iterable[str]] = None
    ):
        pass

    @property
    @abstractmethod
    async def is_professor(self):
        pass

    @abstractmethod
    async def courses(self) -> List['Course']:
        pass

    @abstractmethod
    async def update_info(
            self,
            *,
            update: Dict
    ) -> UpdateResult:
        pass

    @staticmethod
    @abstractmethod
    async def update_email_password(
            *,
            user_id,
            email,
            password: str,
    ) -> bool:
        pass
