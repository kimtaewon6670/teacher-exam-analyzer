from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.models.answer_record_model import AnswerRecord
from app.models.exam_result_model import ExamResult
from app.repositories.answer_record_repository import AnswerRecordRepository
from app.repositories.exam_question_repository import ExamQuestionRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.student_repository import StudentRepository
from app.utils.answer_normalizer import AnswerNormalizer
from app.utils.constants import CORRECT, WRONG


class ResultInputService:
    """Core logic for result input, validation, answer comparison, and persistence."""

    SAMPLE_EXAMS = [
        {"id": 1, "name": "2024년 1학기 중간고사"},
        {"id": 2, "name": "2024년 1학기 기말고사"},
    ]
    SAMPLE_CLASSES = [
        {"id": "1-1", "name": "1학년 1반"},
        {"id": "1-2", "name": "1학년 2반"},
        {"id": "1-3", "name": "1학년 3반"},
    ]
    SAMPLE_STUDENTS = [
        {"id": 1, "name": "김민서", "student_id": "2024001", "class_id": "1-1"},
        {"id": 2, "name": "이서준", "student_id": "2024002", "class_id": "1-1"},
        {"id": 3, "name": "박지우", "student_id": "2024003", "class_id": "1-2"},
    ]
    SAMPLE_SUMMARY = {"question_count": 10, "subject": "영어", "exam_date": "2024-05-20"}

    def __init__(
        self,
        exam_repository: Any = ExamRepository,
        student_repository: Any = StudentRepository,
        exam_question_repository: Any = ExamQuestionRepository,
        question_repository: Any = QuestionRepository,
        result_repository: Any = ResultRepository,
        answer_record_repository: Any = AnswerRecordRepository,
    ) -> None:
        self.exam_repository = exam_repository
        self.student_repository = student_repository
        self.exam_question_repository = exam_question_repository
        self.question_repository = question_repository
        self.result_repository = result_repository
        self.answer_record_repository = answer_record_repository

    def get_initial_view_data(self) -> dict[str, list[dict[str, Any]]]:
        """Return option data for the result input View."""
        exams = self._get_exam_options()
        students = self._get_student_options()
        classes = self._get_class_options(exams, students)

        return {
            "exams": exams,
            "classes": classes,
            "students": students,
        }

    def get_exam_summary(self, exam_id: Any) -> dict[str, Any]:
        if exam_id is None:
            return dict(self.SAMPLE_SUMMARY)

        try:
            exam = self.exam_repository.read(exam_id)
            if exam:
                question_count = self.exam_question_repository.count_by_exam(exam_id)
                return {
                    "question_count": question_count or exam.total_questions or 0,
                    "subject": exam.description or exam.exam_name or "-",
                    "exam_date": exam.exam_date or "-",
                }
        except Exception:
            pass

        return dict(self.SAMPLE_SUMMARY)

    def get_question_count(self, exam_id: Any) -> int:
        summary = self.get_exam_summary(exam_id)
        return self._to_int(summary.get("question_count"), self.SAMPLE_SUMMARY["question_count"])

    def get_students_by_class(self, class_id: Any) -> list[dict[str, Any]]:
        if class_id in (None, ""):
            return self._get_student_options()

        try:
            students = self.student_repository.read_by_class(str(class_id), active_only=True)
            if students:
                return [self._student_to_option(student) for student in students]
        except Exception:
            pass

        return [
            student
            for student in self.SAMPLE_STUDENTS
            if student.get("class_id") == class_id or class_id in (None, "")
        ]

    def validate_input(
        self,
        exam_id: Any,
        student_id: Any,
        answers: dict[Any, Any],
    ) -> tuple[bool, str]:
        if exam_id is None:
            return False, "시험을 선택해주세요."
        if student_id is None:
            return False, "학생을 선택해주세요."

        question_count = self.get_question_count(exam_id)
        normalized_answers = self._normalize_answer_map(answers)
        if not normalized_answers:
            return False, "입력된 답안이 없습니다."

        missing_numbers = [
            question_number
            for question_number in range(1, question_count + 1)
            if not normalized_answers.get(question_number)
        ]
        if missing_numbers:
            preview = ", ".join(str(number) for number in missing_numbers[:5])
            suffix = "..." if len(missing_numbers) > 5 else ""
            return False, f"미입력 문항이 있습니다: {preview}{suffix}"

        return True, f"입력값 검증 완료: 총 {question_count}문항"

    def grade_answers(
        self,
        exam_id: Any,
        student_id: Any,
        answers: dict[Any, Any],
        save_result: bool = True,
    ) -> dict[str, Any]:
        is_valid, message = self.validate_input(exam_id, student_id, answers)
        if not is_valid:
            return {"success": False, "message": message}

        normalized_answers = self._normalize_answer_map(answers)
        question_specs = self._get_question_specs(exam_id)

        correct_count = 0
        answer_records: list[AnswerRecord] = []
        detail_rows = []

        for question_number, spec in enumerate(question_specs, start=1):
            student_answer = normalized_answers.get(question_number, "")
            is_correct = AnswerNormalizer.compare_answers(
                student_answer,
                spec["correct_answer"],
                spec.get("acceptable_answers"),
            )
            correct_count += 1 if is_correct else 0

            answer_records.append(
                AnswerRecord(
                    exam_id=int(exam_id),
                    student_id=int(student_id),
                    question_id=int(spec["question_id"]),
                    student_answer=student_answer,
                    correct_answer=spec["correct_answer"],
                    is_correct=CORRECT if is_correct else WRONG,
                )
            )
            detail_rows.append(
                {
                    "question_number": question_number,
                    "student_answer": student_answer,
                    "correct_answer": spec["correct_answer"],
                    "is_correct": is_correct,
                }
            )

        total_count = len(question_specs)
        wrong_count = total_count - correct_count
        score = self.calculate_score(correct_count, total_count)
        accuracy = self.calculate_accuracy(correct_count, total_count)
        result = ExamResult(
            exam_id=int(exam_id),
            student_id=int(student_id),
            correct_count=correct_count,
            wrong_count=wrong_count,
            score=score,
            accuracy=accuracy,
        )

        saved = False
        if save_result and not self._is_sample_question_specs(question_specs):
            if self.result_repository.read_by_exam_and_student(int(exam_id), int(student_id)):
                return {
                    "success": False,
                    "message": "이미 저장된 시험 결과가 있습니다.",
                    "result": result,
                    "details": detail_rows,
                }
            result.result_id = self.result_repository.create(result)
            self.answer_record_repository.create_batch(answer_records)
            saved = True

        message_prefix = "채점 및 저장 완료" if saved else "채점 완료"
        return {
            "success": True,
            "message": (
                f"{message_prefix}: {correct_count}/{total_count}개 정답, "
                f"점수 {score:.1f}점"
            ),
            "result": result,
            "details": detail_rows,
            "saved": saved,
        }

    def parse_csv_file(self, file_path: str) -> list[dict[str, str]]:
        path = Path(file_path)
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            return [dict(row) for row in csv.DictReader(csv_file)]

    @staticmethod
    def calculate_score(correct_count: int, total_questions: int) -> float:
        if total_questions <= 0:
            return 0.0
        return round((correct_count / total_questions) * 100, 2)

    @staticmethod
    def calculate_accuracy(correct_count: int, total_questions: int) -> float:
        if total_questions <= 0:
            return 0.0
        return round(correct_count / total_questions, 4)

    def _get_exam_options(self) -> list[dict[str, Any]]:
        try:
            exams = self.exam_repository.read_all()
            if exams:
                return [
                    {"id": exam.exam_id, "name": exam.exam_name}
                    for exam in exams
                    if exam.exam_id is not None
                ]
        except Exception:
            pass

        # TODO: Repository 연결이 안정화되면 화면 확인용 샘플데이터 제거.
        return list(self.SAMPLE_EXAMS)

    def _get_student_options(self) -> list[dict[str, Any]]:
        try:
            students = self.student_repository.read_all(active_only=True)
            if students:
                return [self._student_to_option(student) for student in students]
        except Exception:
            pass

        # TODO: Repository 연결이 안정화되면 화면 확인용 샘플데이터 제거.
        return list(self.SAMPLE_STUDENTS)

    def _get_class_options(
        self,
        exams: list[dict[str, Any]],
        students: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        class_ids = []

        try:
            for exam in self.exam_repository.read_all():
                if exam.target_class and exam.target_class not in class_ids:
                    class_ids.append(exam.target_class)
        except Exception:
            pass

        for student in students:
            class_id = student.get("class_id")
            if class_id and class_id not in class_ids:
                class_ids.append(class_id)

        if class_ids:
            return [{"id": class_id, "name": str(class_id)} for class_id in class_ids]

        # TODO: 별도 Class Repository가 추가되면 여기에서 반 목록을 조회하도록 교체.
        return list(self.SAMPLE_CLASSES)

    def _get_question_specs(self, exam_id: Any) -> list[dict[str, Any]]:
        try:
            exam_questions = self.exam_question_repository.read_by_exam(int(exam_id))
            specs = []
            for exam_question in exam_questions:
                question = self.question_repository.read(exam_question.question_id)
                if not question:
                    continue
                specs.append(
                    {
                        "question_id": question.question_id,
                        "correct_answer": question.answer_text,
                        "acceptable_answers": question.acceptable_answers,
                        "is_sample": False,
                    }
                )
            if specs:
                return specs
        except Exception:
            pass

        return self._get_sample_question_specs(self.get_question_count(exam_id))

    def _get_sample_question_specs(self, question_count: int) -> list[dict[str, Any]]:
        # TODO: 실제 시험 문항 Repository 연결 후 제거할 화면 확인용 샘플 정답.
        return [
            {
                "question_id": question_number,
                "correct_answer": str(((question_number - 1) % 4) + 1),
                "acceptable_answers": None,
                "is_sample": True,
            }
            for question_number in range(1, question_count + 1)
        ]

    def _is_sample_question_specs(self, question_specs: list[dict[str, Any]]) -> bool:
        return any(spec.get("is_sample") for spec in question_specs)

    def _student_to_option(self, student: Any) -> dict[str, Any]:
        return {
            "id": student.student_id,
            "name": student.name,
            "student_id": student.student_number,
            "class_id": student.class_name,
        }

    def _normalize_answer_map(self, answers: dict[Any, Any]) -> dict[int, str]:
        normalized = {}
        for question_number, answer in (answers or {}).items():
            try:
                key = int(question_number)
            except (TypeError, ValueError):
                continue
            normalized[key] = str(answer or "").strip()
        return normalized

    def _to_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
