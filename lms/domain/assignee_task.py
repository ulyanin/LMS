# pylint: disable=too-few-public-methods

from typing import Optional, Iterable


class AssigneeTask:
    def __init__(self, *, name, course_id, start_time, end_time, description):
        self.name = name
        self.course_id = course_id
        self.start_time = start_time
        self.end_time = end_time
        self.description = description

    async def get_info(
            self, *,
            properties: Optional[Iterable[str]] = None
    ):
        info = {
            'name': self.name,
            'course_id': self.course_id,
            'description': self.description,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
        }
        if not properties:
            return info
        new_info = {}
        for key in info:
            if key in properties:
                new_info[key] = info[key]
        return new_info
