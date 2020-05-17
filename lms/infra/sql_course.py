from typing import Dict, Optional, Iterable, Any, List

from lms.domain.course import Course
from lms.domain.course_material import CourseMaterial
from lms.domain.professor import Professor
from lms.domain.student import Student

import lms.infra.db.postgres_executor as pe
import lms.infra.sql_professor as sql_professor
import lms.infra.sql_student as sql_student


class SqlCourse(Course):
    async def get_professors(self) -> List[Professor]:
        query = '''SELECT course_id, professor_id FROM course_to_professor WHERE course_id = $1'''
        records = await pe.fetch(
            query=query,
            params=(self.course_id,)
        )
        if not records:
            return []
        professors = []
        for record in records:
            professor_id = record.get('professor_id')
            assert professor_id
            professors.append(sql_professor.SqlProfessor(user_id=professor_id))
        return professors

    async def get_editors(self) -> List[Student]:
        query = '''SELECT course_id, student_id FROM course_to_editor WHERE course_id = $1'''
        records = await pe.fetch(
            query=query,
            params=(self.course_id,)
        )
        if not records:
            return []
        editors = []
        for record in records:
            student_id = record.get('student_id')
            assert student_id
            editors.append(sql_student.SqlStudent(user_id=student_id))
        return editors

    async def get_materials(self) -> List[CourseMaterial]:
        return []

    async def get_info(
            self,
            *,
            properties: Optional[Iterable[str]] = None
    ) -> Optional[Dict[str, Any]]:
        if properties is None:
            properties = self.PROPERTIES
        query = '''SELECT course_id, name, description FROM course WHERE course_id = $1'''
        record = await pe.fetch_row(
            query=query,
            params=(self.course_id,)
        )
        if record is None:
            return None
        info = {}
        for key in record.keys():
            if key in properties:
                info[key] = record.get(key)
        additional_info = await self.get_additional_info(properties)
        info.update(additional_info)
        return info
