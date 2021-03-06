from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable, List, Optional, Any

from lms.domain.course_material import CourseMaterial
from lms.domain.assignee_task import AssigneeTask
from lms.domain.professor import Professor
from lms.domain.student import Student


class Course(metaclass=ABCMeta):
    NATIVE_PROPERTIES = (
        'course_id',
        'name',
        'description',
    )
    ADDITIONAL_PROPERTIES = (
        'professors',
        'editors',
        'materials',
        'assignees',
    )
    PROPERTIES = NATIVE_PROPERTIES + ADDITIONAL_PROPERTIES

    def __init__(self, *, course_id):
        self.course_id = course_id

    def __bool__(self):
        return self.course_id is not None

    @abstractmethod
    async def get_professors(self) -> List[Professor]:
        pass

    @abstractmethod
    async def get_editors(self) -> List[Student]:
        pass

    @abstractmethod
    async def get_materials(self) -> List[CourseMaterial]:
        pass

    @abstractmethod
    async def get_assignees(self) -> List[AssigneeTask]:
        return []

    async def _apply_getinfo(self, items: List[Any], properties=None):
        # ['user_id', 'name', 'email', 'group_name', 'description']
        return [
            await item.get_info(properties=properties)
            for item in items
        ]

    async def get_additional_info(self, properties: List[str]) -> Dict[str, Any]:
        info = {}
        if 'professors' in properties:
            info['professors'] = await self._apply_getinfo(
                items=await self.get_professors(),
                properties=['user_id', 'name', 'email'],
            )
        if 'editors' in properties:
            info['editors'] = await self._apply_getinfo(
                items=await self.get_editors(),
                properties=['user_id', 'name', 'email'],
            )
        if 'materials' in properties:
            info['materials'] = await self._apply_getinfo(
                items=await self.get_materials()
            )
        if 'assignees' in properties:
            info['assignees'] = await self._apply_getinfo(
                items=await self.get_assignees()
            )
        return info

    @abstractmethod
    async def get_info(
            self,
            *,
            properties: Optional[Iterable[str]] = None
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_assignees_grouped(self, *, assignee_name) -> Dict[str, List[Any]]:
        pass

    @abstractmethod
    async def check_assigned(self, *, user_id) -> bool:
        pass

    @abstractmethod
    async def submit_assignee(self, *, assignee_name, student_id, solution: str) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    async def resolve_assignee_course(*, assignee_name) -> Optional['Course']:
        pass
