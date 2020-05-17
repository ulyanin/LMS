from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable, List, Optional, Any

from lms.domain.course_material import CourseMaterial
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

    @staticmethod
    async def get_assignees():
        return []

    async def _apply_getinfo(self, items: List[Any]):
        return [
            await item.get_info(properties=['user_id', 'name', 'email', 'group_name'])
            for item in items
        ]

    async def get_additional_info(self, properties: List[str]) -> Dict[str, Any]:
        info = {}
        if 'professors' in properties:
            info['professors'] = await self.get_professors()
        if 'editors' in properties:
            info['editors'] = await self.get_editors()
        if 'materials' in properties:
            info['materials'] = await self.get_materials()
        if 'assignees' in properties:
            info['assignees'] = await self.get_assignees()
        for key in info:
            info[key] = await self._apply_getinfo(info[key])
        return info

    @abstractmethod
    async def get_info(
            self,
            *,
            properties: Optional[Iterable[str]] = None
    ) -> Optional[Dict[str, Any]]:
        pass
