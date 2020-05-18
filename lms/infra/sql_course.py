from collections import defaultdict
from typing import Dict, Optional, Iterable, Any, List

from lms.domain.course import Course
from lms.domain.course_material import CourseMaterial
from lms.domain.assignee_task import AssigneeTask
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
        query = '''SELECT name, course_id, description, add_time
            FROM course_material WHERE course_id = $1'''
        records = await pe.fetch(
            query=query,
            params=(self.course_id,)
        )
        if not records:
            return []
        materials = []
        for record in records:
            material = CourseMaterial(
                name=record.get('name'),
                course_id=record.get('course_id'),
                description=record.get('description'),
                add_time=record.get('add_time'),
            )
            materials.append(material)
        return materials

    async def get_assignees(self) -> List[AssigneeTask]:
        query = '''SELECT name, course_id, start_time, end_time, description
            FROM assignee_task WHERE course_id = $1'''
        records = await pe.fetch(
            query=query,
            params=(self.course_id,)
        )
        if not records:
            return []
        assignees = []
        for record in records:
            assignee = AssigneeTask(
                name=record.get('name'),
                course_id=record.get('course_id'),
                description=record.get('description'),
                start_time=record.get('start_time'),
                end_time=record.get('end_time'),
            )
            assignees.append(assignee)
        return assignees

    async def get_submitted_assignees(self, *, assignee_name) -> Dict[int, Any]:
        query = '''SELECT 
            student.user_id as user_id, 
            "as".submit_time as submit_time,
            "as".solution as solution
        FROM assignee_task
            JOIN assignee_submit "as" on assignee_task.name = "as".assignee_name
            JOIN student on "as".student_id = student.user_id
        WHERE assignee_task.name = $1 AND assignee_task.course_id = $2'''
        records = await pe.fetch(
            query=query,
            params=(assignee_name, self.course_id)
        )
        submits = dict()
        for record in records:
            user_id = record.get('user_id')
            submit_time = record.get('submit_time')
            solution = record.get('solution')
            submits[user_id] = {
                'submit_time': str(submit_time),
                'solution': solution,
            }
        return submits

    async def get_assignees_grouped(self, *, assignee_name) -> Dict[str, List[Any]]:
        query_students = '''SELECT
            users.user_id as user_id, 
            sg.group_name as group_name,
            users.email as email,
            users.name as name
        FROM assignee_task
            JOIN course c on assignee_task.course_id = c.course_id
            JOIN group_to_course gtc on c.course_id = gtc.course_id
            JOIN student_group sg on gtc.group_name = sg.group_name
            JOIN student on sg.group_name = student.group_name
            JOIN users on student.user_id = users.user_id
        WHERE assignee_task.name = $1 AND assignee_task.course_id = $2'''
        group2students = defaultdict(list)
        records = await pe.fetch(
            query=query_students,
            params=(assignee_name, self.course_id)
        )
        submitted_assignees = await self.get_submitted_assignees(assignee_name=assignee_name)
        for record in records:
            user_id = record.get('user_id')
            group_name = record.get('group_name')
            email = record.get('email')
            name = record.get('name')
            group2students[group_name].append({
                'user_id': user_id,
                'group_name': group_name,
                'email': email,
                'name': name,
                'submition': submitted_assignees.get(user_id, None),
            })
        return group2students

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
