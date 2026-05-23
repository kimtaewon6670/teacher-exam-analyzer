from __future__ import annotations

from typing import Any

from app.models.student_model import Student
from app.repositories.student_repository import StudentRepository


class StudentController:
    def create_student(self, name: str, student_number: str, class_name: str) -> int:
        student = Student(
            name=name.strip(),
            student_number=student_number.strip(),
            class_name=class_name.strip(),
            is_active=1,
        )
        return StudentRepository.create(student)

    def get_students(self) -> list[dict[str, Any]]:
        students = StudentRepository.read_all(active_only=False)
        return [self._to_view_data(student) for student in students]

    def search_students(self, keyword: str = "", class_name: str = "") -> list[dict[str, Any]]:
        normalized_keyword = keyword.strip().lower()
        normalized_class_name = class_name.strip()

        students = StudentRepository.read_all(active_only=False)
        filtered_students = []
        for student in students:
            matches_keyword = (
                not normalized_keyword
                or normalized_keyword in student.name.lower()
                or normalized_keyword in student.student_number.lower()
            )
            matches_class = not normalized_class_name or student.class_name == normalized_class_name

            if matches_keyword and matches_class:
                filtered_students.append(student)

        return [self._to_view_data(student) for student in filtered_students]

    def update_student(self, student_id: int, name: str, student_number: str, class_name: str) -> bool:
        existing_student = StudentRepository.read(student_id)
        if existing_student is None:
            return False

        student = Student(
            student_id=student_id,
            name=name.strip(),
            student_number=student_number.strip(),
            class_name=class_name.strip(),
            is_active=existing_student.is_active,
            created_at=existing_student.created_at,
        )
        return StudentRepository.update(student)

    def deactivate_student(self, student_id: int) -> bool:
        return StudentRepository.deactivate(student_id)

    def activate_student(self, student_id: int) -> bool:
        return StudentRepository.activate(student_id)

    def _to_view_data(self, student: Student) -> dict[str, Any]:
        return {
            "id": student.student_id,
            "name": student.name,
            "student_id": student.student_number,
            "class_name": student.class_name,
            "status": "활성" if student.is_active else "비활성",
        }
