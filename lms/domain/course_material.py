# pylint: disable=too-few-public-methods

from typing import Optional, Iterable


class CourseMaterial:
    PROPERTIES = (
        'course_id',
        'name',
        'description',
        'add_time',
    )

    def __init__(self, *, name, course_id, description, add_time):
        self.name = name
        self.course_id = course_id
        self.description = description
        self.add_time = add_time

    async def get_info(
            self, *,
            properties: Optional[Iterable[str]] = None
    ):
        info = {
            'name': self.name,
            'course_id': self.course_id,
            'description': self.description,
            'add_time': str(self.add_time),
        }
        if not properties:
            return info
        new_info = {}
        for key in info:
            if key in properties:
                new_info[key] = info[key]
        return new_info
