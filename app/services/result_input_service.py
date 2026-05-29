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

    EMPTY_SUMMARY = {"question_count": 0, "subject": "-", "exam_date": "-"}

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
        self._answer_input_state: dict[str, Any] = {}

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
            return dict(self.EMPTY_SUMMARY)

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

        return dict(self.EMPTY_SUMMARY)

    def get_question_count(self, exam_id: Any) -> int:
        summary = self.get_exam_summary(exam_id)
        return self._to_int(summary.get("question_count"), 0)

    def get_students_by_class(self, class_id: Any) -> list[dict[str, Any]]:
        if class_id in (None, ""):
            return self._get_student_options()

        try:
            students = self.student_repository.read_by_class(str(class_id), active_only=True)
            if students:
                return [self._student_to_option(student) for student in students]
        except Exception:
            pass

        normalized_class_id = self._normalize_class_name(class_id)
        try:
            students = [
                student
                for student in self.student_repository.read_all(active_only=True)
                if self._normalize_class_name(student.class_name) == normalized_class_id
            ]
            if students:
                students.sort(key=lambda student: str(student.student_number))
                return [self._student_to_option(student) for student in students]
        except Exception:
            pass

        return []

    def clear_answer_input_state(self) -> None:
        self._answer_input_state = {}

    def get_student_answers(self, exam_id: Any, student_id: Any) -> dict[int, str]:
        if exam_id in (None, "") or student_id in (None, ""):
            return {}

        try:
            exam_id_int = int(exam_id)
            student_id_int = int(student_id)
        except (TypeError, ValueError):
            return {}

        try:
            records = self.answer_record_repository.read_by_exam_and_student(
                exam_id_int,
                student_id_int,
            )
        except Exception:
            return {}

        question_order = self._get_question_order_map(exam_id_int)
        answers: dict[int, str] = {}
        for record in records:
            question_number = question_order.get(record.question_id)
            if question_number is not None:
                answers[question_number] = record.student_answer or ""

        self._answer_input_state = {
            "exam_id": exam_id_int,
            "student_id": student_id_int,
            "answers": dict(answers),
        }
        return answers

    def load_answers_for_student(self, exam_id: Any, student_id: Any) -> dict[int, str]:
        self.clear_answer_input_state()
        return self.get_student_answers(exam_id, student_id)

    def save_student_answers(
        self,
        exam_id: Any,
        student_id: Any,
        answers: dict[Any, Any],
    ) -> dict[str, Any]:
        return self.grade_answers(exam_id, student_id, answers, save_result=True)

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
        if question_count <= 0:
            return False, "선택한 시험에 저장된 문항이 없습니다."

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
        if not question_specs:
            return {
                "success": False,
                "message": "선택한 시험의 문항 정보를 찾을 수 없습니다.",
            }

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
            try:
                if hasattr(self.result_repository, "replace_for_student"):
                    self.result_repository.replace_for_student(result)
                else:
                    if hasattr(self.result_repository, "delete_by_exam_and_student"):
                        self.result_repository.delete_by_exam_and_student(int(exam_id), int(student_id))
                    result.result_id = self.result_repository.create(result)

                if hasattr(self.answer_record_repository, "replace_for_student"):
                    self.answer_record_repository.replace_for_student(
                        int(exam_id),
                        int(student_id),
                        answer_records,
                    )
                else:
                    if hasattr(self.answer_record_repository, "delete_by_exam_and_student"):
                        self.answer_record_repository.delete_by_exam_and_student(
                            int(exam_id),
                            int(student_id),
                        )
                    self.answer_record_repository.create_batch(answer_records)
            except Exception as exc:
                return {
                    "success": False,
                    "message": f"채점 결과 저장 중 오류가 발생했습니다: {exc}",
                    "result": result,
                    "details": detail_rows,
                }
            saved = True
            self._answer_input_state = {
                "exam_id": int(exam_id),
                "student_id": int(student_id),
                "answers": dict(normalized_answers),
            }

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

    def run_auto_grading(self, exam_id: Any, class_id: Any = None) -> dict[str, Any]:
        if exam_id in (None, ""):
            return {"success": False, "message": "시험을 선택해 주세요.", "results": []}

        try:
            exam_id_int = int(exam_id)
        except (TypeError, ValueError):
            return {"success": False, "message": "시험 ID가 올바르지 않습니다.", "results": []}

        students = self.get_students_by_class(class_id)
        graded_results = []
        failed_results = []

        for student in students:
            student_id = student.get("id")
            saved_answers = self.get_student_answers(exam_id_int, student_id)
            if not saved_answers:
                continue

            result = self.grade_answers(exam_id_int, student_id, saved_answers, save_result=True)
            if result.get("success"):
                graded_results.append(result)
            else:
                failed_results.append({"student_id": student_id, "message": result.get("message", "")})

        if not graded_results:
            return {
                "success": False,
                "message": "채점할 학생 답안이 없습니다.",
                "results": [],
                "failed": failed_results,
            }

        return {
            "success": True,
            "message": f"자동 채점 완료: {len(graded_results)}명",
            "results": graded_results,
            "failed": failed_results,
        }

    def get_grading_result(self, exam_id: Any) -> dict[str, Any]:
        return self.build_grading_result_view_data(exam_id)

    def get_grading_result_by_student(self, exam_id: Any, student_id: Any) -> dict[str, Any]:
        return self.build_grading_result_view_data(exam_id, student_id)

    def build_grading_result_view_data(
        self,
        exam_id: Any,
        student_id: Any = None,
    ) -> dict[str, Any]:
        if exam_id in (None, ""):
            return {"success": False, "message": "시험을 선택해 주세요."}

        try:
            exam_id_int = int(exam_id)
            student_id_int = int(student_id) if student_id not in (None, "") else None
        except (TypeError, ValueError):
            return {"success": False, "message": "채점 결과 조회 조건이 올바르지 않습니다."}

        try:
            exam = self.exam_repository.read(exam_id_int)
            if student_id_int is None:
                results = self.result_repository.read_by_exam(exam_id_int)
            else:
                result = self.result_repository.read_by_exam_and_student(exam_id_int, student_id_int)
                results = [result] if result else []
        except Exception as exc:
            return {"success": False, "message": f"채점 결과 조회 중 오류가 발생했습니다: {exc}"}

        if not results:
            return {"success": False, "message": "채점 결과가 없습니다."}

        question_specs = self._get_question_specs(exam_id_int)
        question_order = {
            int(spec["question_id"]): index
            for index, spec in enumerate(question_specs, start=1)
        }
        question_by_id = {
            int(spec["question_id"]): spec
            for spec in question_specs
            if spec.get("question_id") is not None
        }

        student_rows = []
        for result in results:
            student = self._read_student(result.student_id)
            answer_records = self.answer_record_repository.read_by_exam_and_student(
                exam_id_int,
                int(result.student_id),
            )
            detail_rows = self._build_result_details(answer_records, question_order, question_by_id)
            total_questions = len(question_specs) or (result.correct_count or 0) + (result.wrong_count or 0)
            student_rows.append(
                {
                    "student_id": result.student_id,
                    "student_name": getattr(student, "name", ""),
                    "student_number": getattr(student, "student_number", ""),
                    "class_name": getattr(student, "class_name", ""),
                    "exam_name": getattr(exam, "exam_name", ""),
                    "total_questions": total_questions,
                    "correct_count": result.correct_count or 0,
                    "wrong_count": result.wrong_count or 0,
                    "score": result.score or 0,
                    "accuracy": result.accuracy or 0,
                    "details": detail_rows,
                }
            )

        return {
            "success": True,
            "message": "채점 결과를 불러왔습니다.",
            "exam": {
                "exam_id": exam_id_int,
                "exam_name": getattr(exam, "exam_name", ""),
                "class_name": getattr(exam, "target_class", ""),
                "exam_date": getattr(exam, "exam_date", ""),
                "total_questions": len(question_specs) or getattr(exam, "total_questions", 0),
            },
            "students": student_rows,
        }

    def parse_csv_file(self, file_path: str) -> list[dict[str, str]]:
        path = Path(file_path)
        last_error: Exception | None = None
        for encoding in ("utf-8-sig", "cp949", "euc-kr"):
            try:
                with path.open("r", encoding=encoding, newline="") as csv_file:
                    return [self._normalize_csv_row(dict(row)) for row in csv.DictReader(csv_file)]
            except UnicodeDecodeError as exc:
                last_error = exc

        if last_error is not None:
            raise last_error
        return []

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

        return []

    def _get_student_options(self) -> list[dict[str, Any]]:
        try:
            students = self.student_repository.read_all(active_only=True)
            if students:
                return [self._student_to_option(student) for student in students]
        except Exception:
            pass

        return []

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
            if class_id and self._normalize_class_name(class_id) not in {
                self._normalize_class_name(existing_class_id) for existing_class_id in class_ids
            }:
                class_ids.append(class_id)

        if class_ids:
            return [{"id": class_id, "name": str(class_id)} for class_id in class_ids]

        return []

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
                        "question_text": question.question_text,
                        "correct_answer": question.answer_text,
                        "acceptable_answers": question.acceptable_answers,
                        "explanation": question.explanation or "",
                        "category": question.category,
                        "sub_category": question.sub_category,
                        "difficulty": question.difficulty,
                        "is_sample": False,
                    }
                )
            if specs:
                return specs
        except Exception:
            pass

        return []

    def _get_question_order_map(self, exam_id: Any) -> dict[int, int]:
        specs = self._get_question_specs(exam_id)
        return {
            int(spec["question_id"]): index
            for index, spec in enumerate(specs, start=1)
            if spec.get("question_id") is not None
        }

    def _read_student(self, student_id: Any) -> Any:
        try:
            return self.student_repository.read(int(student_id))
        except Exception:
            return None

    def _build_result_details(
        self,
        answer_records: list[Any],
        question_order: dict[int, int],
        question_by_id: dict[int, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        rows = []
        for record in answer_records:
            question_id = int(record.question_id)
            spec = question_by_id.get(question_id, {})
            rows.append(
                {
                    "question_no": question_order.get(question_id, len(rows) + 1),
                    "question_number": question_order.get(question_id, len(rows) + 1),
                    "question_id": question_id,
                    "question_text": spec.get("question_text", ""),
                    "correct_answer": record.correct_answer,
                    "student_answer": record.student_answer,
                    "is_correct": record.is_correct == CORRECT,
                    "score": 1 if record.is_correct == CORRECT else 0,
                    "explanation": spec.get("explanation", ""),
                }
            )

        rows.sort(key=lambda row: row["question_no"])
        return rows

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

    def _normalize_csv_row(self, row: dict[str, str]) -> dict[str, str]:
        normalized = {}
        for key, value in row.items():
            clean_key = str(key or "").strip()
            clean_value = str(value or "").strip()
            lower_key = clean_key.lower().replace(" ", "")
            if lower_key in {"학번", "studentnumber", "student_no", "studentno"}:
                normalized["student_id"] = clean_value
                continue
            if lower_key.startswith("문항") and lower_key.endswith("번"):
                number = lower_key.removeprefix("문항").removesuffix("번")
                if number.isdigit():
                    normalized[f"q{number}"] = clean_value
                    continue
            if lower_key.endswith("번") and lower_key[:-1].isdigit():
                normalized[f"q{lower_key[:-1]}"] = clean_value
                continue
            normalized[clean_key] = clean_value
        return normalized

    def _to_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _normalize_class_name(self, value: Any) -> str:
        return str(value or "").replace(" ", "").strip()
