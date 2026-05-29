from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.repositories.answer_record_repository import AnswerRecordRepository
from app.repositories.exam_question_repository import ExamQuestionRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.student_repository import StudentRepository
from app.utils.constants import CORRECT


class AnalysisService:
    """Core analysis logic for exam results and weakness summaries."""

    def __init__(
        self,
        exam_repository: Any = ExamRepository,
        student_repository: Any = StudentRepository,
        result_repository: Any = ResultRepository,
        answer_record_repository: Any = AnswerRecordRepository,
        exam_question_repository: Any = ExamQuestionRepository,
        question_repository: Any = QuestionRepository,
    ) -> None:
        self.exam_repository = exam_repository
        self.student_repository = student_repository
        self.result_repository = result_repository
        self.answer_record_repository = answer_record_repository
        self.exam_question_repository = exam_question_repository
        self.question_repository = question_repository

    def get_initial_view_data(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "exams": self.get_exam_options(),
            "classes": self.get_class_options(),
        }

    def get_exam_options(self) -> list[dict[str, Any]]:
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

    def get_class_options(self) -> list[dict[str, Any]]:
        class_ids = []
        normalized_class_ids = set()
        try:
            for exam in self.exam_repository.read_all():
                if exam.target_class and self._normalize_class_name(exam.target_class) not in normalized_class_ids:
                    class_ids.append(exam.target_class)
                    normalized_class_ids.add(self._normalize_class_name(exam.target_class))
        except Exception:
            pass

        try:
            for student in self.student_repository.read_all(active_only=True):
                normalized_class_name = self._normalize_class_name(student.class_name)
                if student.class_name and normalized_class_name not in normalized_class_ids:
                    class_ids.append(student.class_name)
                    normalized_class_ids.add(normalized_class_name)
        except Exception:
            pass

        if class_ids:
            return [{"id": class_id, "name": str(class_id)} for class_id in class_ids]

        return []

    def analyze(self, filters: dict[str, Any]) -> dict[str, Any]:
        exam_id = filters.get("exam_id")
        class_id = filters.get("class_id")

        if exam_id is None:
            return self._empty_analysis()

        try:
            results = self.result_repository.read_by_exam(int(exam_id))
            if class_id:
                results = self._filter_results_by_class(results, class_id)

            answer_records = self.answer_record_repository.read_by_exam(int(exam_id))
            if class_id:
                student_ids = {result.student_id for result in results}
                answer_records = [
                    record for record in answer_records if record.student_id in student_ids
                ]

            question_map = self._get_question_map(int(exam_id), answer_records)
            if results or answer_records:
                return self._build_analysis(results, answer_records, question_map)
        except Exception:
            pass

        return self._empty_analysis()

    def get_dashboard_summary(self, exam_id: Any, class_id: Any = None) -> dict[str, Any]:
        return self.build_dashboard_data(exam_id, class_id).get("summary", {})

    def get_question_accuracy_stats(self, exam_id: Any, class_id: Any = None) -> list[dict[str, Any]]:
        return self.build_dashboard_data(exam_id, class_id).get("question_accuracy", [])

    def get_category_accuracy_stats(self, exam_id: Any, class_id: Any = None) -> list[dict[str, Any]]:
        return self.build_dashboard_data(exam_id, class_id).get("category_accuracy", [])

    def get_subcategory_accuracy_top5(self, exam_id: Any, class_id: Any = None) -> list[dict[str, Any]]:
        return self.build_dashboard_data(exam_id, class_id).get("subcategory_accuracy_top5", [])

    def get_difficulty_accuracy_stats(self, exam_id: Any, class_id: Any = None) -> list[dict[str, Any]]:
        return self.build_dashboard_data(exam_id, class_id).get("difficulty_accuracy", [])

    def get_student_result_table(self, exam_id: Any, class_id: Any = None) -> list[dict[str, Any]]:
        return self.build_dashboard_data(exam_id, class_id).get("student_results", [])

    def get_registered_students_for_dashboard(self, class_id: Any = None) -> list[Any]:
        return self._get_registered_students(class_id)

    def get_exam_question_count(self, exam_id: Any) -> int:
        exam_id_int = self._resolve_exam_id(exam_id)
        if exam_id_int is None:
            return 0

        try:
            exam_questions = self.exam_question_repository.read_by_exam(exam_id_int)
            if exam_questions:
                return len(exam_questions)
        except Exception:
            pass

        try:
            exam = self.exam_repository.read(exam_id_int)
            return int(getattr(exam, "total_questions", 0) or 0)
        except Exception:
            return 0

    def build_dashboard_data(
        self,
        exam_id: Any,
        class_id: Any = None,
        exam_date: Any = None,
    ) -> dict[str, Any]:
        if exam_id in (None, ""):
            return self._empty_dashboard("시험을 선택해 주세요.", exam_id, class_id, exam_date)

        exam_id_int = self._resolve_exam_id(exam_id)
        if exam_id_int is None:
            return self._empty_dashboard("시험 ID가 올바르지 않습니다.", exam_id, class_id, exam_date)
        exam_date = self._normalize_exam_date(exam_date)

        try:
            exam = self.exam_repository.read(exam_id_int)
            if not exam:
                return self._empty_dashboard("시험 정보를 찾을 수 없습니다.", exam_id_int, class_id, exam_date)

            selected_class_id = class_id or getattr(exam, "target_class", "")
            registered_students = self._get_registered_students(selected_class_id)
            registered_student_ids = {
                int(student.student_id)
                for student in registered_students
                if getattr(student, "student_id", None) is not None
            }
            results = self.result_repository.read_by_exam(exam_id_int)
            if registered_student_ids:
                results = [
                    result for result in results if int(result.student_id) in registered_student_ids
                ]
            elif selected_class_id not in (None, ""):
                results = self._filter_results_by_class(results, selected_class_id)

            result_student_ids = {int(result.student_id) for result in results}
            answer_records = self.answer_record_repository.read_by_exam(exam_id_int)
            answer_student_ids = registered_student_ids or result_student_ids
            answer_records = [
                record
                for record in answer_records
                if int(record.student_id) in answer_student_ids
            ]

            exam_questions = self.exam_question_repository.read_by_exam(exam_id_int)
            ordered_question_ids = [int(item.question_id) for item in exam_questions]
            total_questions = len(ordered_question_ids) or int(getattr(exam, "total_questions", 0) or 0)
            question_map = self._get_question_map(exam_id_int, answer_records)
        except Exception as exc:
            return self._empty_dashboard(f"대시보드 데이터 조회 중 오류가 발생했습니다: {exc}", exam_id, class_id, exam_date)

        student_results = self._build_dashboard_student_rows(registered_students, results, total_questions)
        question_accuracy = self._build_dashboard_question_accuracy(
            answer_records,
            ordered_question_ids,
            question_map,
        )
        category_accuracy = self._build_dashboard_group_accuracy(
            answer_records,
            question_map,
            "category",
            "category",
            empty_label="미분류",
        )
        subcategory_accuracy = self._build_dashboard_group_accuracy(
            answer_records,
            question_map,
            "sub_category",
            "sub_category",
            empty_label="미분류",
        )
        difficulty_accuracy = self._build_dashboard_group_accuracy(
            answer_records,
            question_map,
            "difficulty",
            "difficulty",
            empty_label="미분류",
            label_normalizer=self._normalize_difficulty_label,
            sort_order=["쉬움", "보통", "어려움", "미분류"],
        )

        if not (results and answer_records):
            question_accuracy = []
            category_accuracy = []
            subcategory_accuracy = []
            difficulty_accuracy = []

        student_count = len(registered_students)
        total_answers = len(answer_records)
        total_correct = sum(1 for record in answer_records if record.is_correct == CORRECT)
        average_score = self._average([float(result.score or 0) for result in results])
        average_correct_count = self._average([float(result.correct_count or 0) for result in results])

        dashboard = {
            "success": True,
            "message": "대시보드 데이터를 조회했습니다.",
            "filters": {
                "exam_id": exam_id_int,
                "exam_name": getattr(exam, "exam_name", ""),
                "class_id": selected_class_id,
                "class_name": selected_class_id,
                "exam_date": exam_date or getattr(exam, "exam_date", ""),
            },
            "summary": {
                "student_count": student_count,
                "total_questions": total_questions,
                "average_score": round(average_score, 2),
                "overall_accuracy": self._percent(total_correct, total_answers),
                "average_correct_count": round(average_correct_count, 2),
            },
            "question_accuracy": question_accuracy,
            "category_accuracy": category_accuracy,
            "subcategory_accuracy_top5": sorted(
                subcategory_accuracy,
                key=lambda row: (-float(row.get("accuracy", 0)), str(row.get("sub_category", ""))),
            )[:5],
            "difficulty_accuracy": difficulty_accuracy,
            "student_results": student_results,
        }
        dashboard["metrics"] = self._build_dashboard_metrics(dashboard["summary"])
        dashboard["charts"] = self._build_dashboard_chart_payload(
            question_accuracy,
            category_accuracy,
            subcategory_accuracy,
            difficulty_accuracy,
        )
        return dashboard

    def _build_dashboard_student_rows(
        self,
        students: list[Any],
        results: list[Any],
        total_questions: int,
    ) -> list[dict[str, Any]]:
        rows = []
        result_by_student_id = {
            int(result.student_id): result
            for result in results
            if getattr(result, "student_id", None) is not None
        }

        if not students and results:
            students = [self._read_student(result.student_id) for result in results]
            students = [student for student in students if student is not None]

        for student in students:
            student_id = getattr(student, "student_id", None)
            result = result_by_student_id.get(int(student_id)) if student_id is not None else None
            if result is None:
                correct_count = 0
                wrong_count = 0
                score = 0.0
                accuracy = 0.0
            else:
                correct_count = int(result.correct_count or 0)
                wrong_count = int(result.wrong_count or max(total_questions - correct_count, 0))
                score = float(result.score or self._percent(correct_count, total_questions))
                accuracy = float(result.accuracy or 0)
                if accuracy <= 1:
                    accuracy *= 100

            rows.append(
                {
                    "row_no": 0,
                    "student_id": student_id,
                    "student_name": self._get_attr(student, "name", ""),
                    "student_number": self._get_attr(student, "student_number", ""),
                    "correct_count": correct_count,
                    "wrong_count": wrong_count,
                    "score": round(score, 2),
                    "accuracy": round(accuracy, 2),
                }
            )

        if not rows:
            for result in results:
                student = self._read_student(result.student_id)
                correct_count = int(result.correct_count or 0)
                wrong_count = int(result.wrong_count or max(total_questions - correct_count, 0))
                score = float(result.score or self._percent(correct_count, total_questions))
                accuracy = float(result.accuracy or 0)
                if accuracy <= 1:
                    accuracy *= 100

                rows.append(
                    {
                        "row_no": 0,
                        "student_id": result.student_id,
                        "student_name": self._get_attr(student, "name", ""),
                        "student_number": self._get_attr(student, "student_number", ""),
                        "correct_count": correct_count,
                        "wrong_count": wrong_count,
                        "score": round(score, 2),
                        "accuracy": round(accuracy, 2),
                    }
                )

        rows.sort(key=lambda row: (str(row.get("student_name", "")), str(row.get("student_number", ""))))
        for index, row in enumerate(rows, start=1):
            row["row_no"] = index
        return rows

    def _build_dashboard_question_accuracy(
        self,
        answer_records: list[Any],
        ordered_question_ids: list[int],
        question_map: dict[int, Any],
    ) -> list[dict[str, Any]]:
        grouped = self._group_records(answer_records, lambda record: int(record.question_id))
        question_ids = ordered_question_ids or sorted(grouped)
        rows = []

        for index, question_id in enumerate(question_ids, start=1):
            records = grouped.get(question_id, [])
            correct_count = sum(1 for record in records if record.is_correct == CORRECT)
            question = question_map.get(question_id)
            rows.append(
                {
                    "question_no": index,
                    "question_number": index,
                    "question_id": question_id,
                    "question_text": self._get_question_text(question, question_id),
                    "accuracy": self._percent(correct_count, len(records)),
                    "correct_count": correct_count,
                    "total_count": len(records),
                }
            )

        return rows

    def _build_dashboard_group_accuracy(
        self,
        answer_records: list[Any],
        question_map: dict[int, Any],
        question_attr: str,
        output_key: str,
        empty_label: str = "미분류",
        label_normalizer: Any = None,
        sort_order: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        grouped: dict[str, list[Any]] = defaultdict(list)
        for record in answer_records:
            question = question_map.get(record.question_id)
            label = self._get_attr(question, question_attr, empty_label)
            label = str(label or empty_label).strip() or empty_label
            if label_normalizer:
                label = label_normalizer(label)
            grouped[label].append(record)

        rows = []
        for label, records in grouped.items():
            correct_count = sum(1 for record in records if record.is_correct == CORRECT)
            rows.append(
                {
                    output_key: label,
                    "accuracy": self._percent(correct_count, len(records)),
                    "correct_count": correct_count,
                    "total_count": len(records),
                }
            )

        if sort_order:
            order = {label: index for index, label in enumerate(sort_order)}
            rows.sort(key=lambda row: (order.get(row.get(output_key), len(order)), str(row.get(output_key, ""))))
        else:
            rows.sort(key=lambda row: str(row.get(output_key, "")))
        return rows

    def _build_dashboard_metrics(self, summary: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "key": "student_count",
                "label": "응시 학생 수",
                "value": str(summary.get("student_count", 0)),
                "unit": "명",
            },
            {
                "key": "total_questions",
                "label": "총 문항 수",
                "value": str(summary.get("total_questions", 0)),
                "unit": "문항",
            },
            {
                "key": "average_score",
                "label": "반 평균 점수",
                "value": f"{float(summary.get('average_score', 0) or 0):.2f}",
                "unit": "점 /100",
            },
            {
                "key": "overall_accuracy",
                "label": "전체 정답률",
                "value": f"{float(summary.get('overall_accuracy', 0) or 0):.2f}",
                "unit": "%",
            },
            {
                "key": "average_correct_count",
                "label": "평균 정답 수",
                "value": f"{float(summary.get('average_correct_count', 0) or 0):.2f}",
                "unit": "개",
            },
        ]

    def _build_dashboard_chart_payload(
        self,
        question_accuracy: list[dict[str, Any]],
        category_accuracy: list[dict[str, Any]],
        subcategory_accuracy: list[dict[str, Any]],
        difficulty_accuracy: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "question_values": [
                float(row.get("accuracy", 0) or 0)
                for row in question_accuracy
            ],
            "category_values": [
                float(row.get("accuracy", 0) or 0)
                for row in category_accuracy
            ],
            "category_labels": [
                str(row.get("category", ""))
                for row in category_accuracy
            ],
            "subcategory_values": [
                (
                    str(row.get("sub_category", "")),
                    float(row.get("accuracy", 0) or 0),
                )
                for row in sorted(
                    subcategory_accuracy,
                    key=lambda item: (-float(item.get("accuracy", 0) or 0), str(item.get("sub_category", ""))),
                )[:5]
            ],
            "difficulty_values": [
                float(row.get("accuracy", 0) or 0)
                for row in difficulty_accuracy
            ],
            "difficulty_labels": [
                str(row.get("difficulty", ""))
                for row in difficulty_accuracy
            ],
            "donut_colors": ["#3d8be8", "#43bd6e", "#f59a23", "#8c63d9", "#18b6bd"],
        }

    def _normalize_difficulty_label(self, value: Any) -> str:
        normalized = str(value or "").strip().lower()
        if normalized in {"easy", "low", "1", "하", "쉬움"}:
            return "쉬움"
        if normalized in {"medium", "mid", "normal", "2", "중", "보통", "중간"}:
            return "보통"
        if normalized in {"hard", "high", "3", "상", "어려움"}:
            return "어려움"
        return str(value or "미분류").strip() or "미분류"

    def _percent(self, numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    def _resolve_exam_id(self, exam_id: Any) -> int | None:
        try:
            return int(exam_id)
        except (TypeError, ValueError):
            pass

        target_name = str(exam_id or "").strip()
        if not target_name:
            return None

        try:
            for exam in self.exam_repository.read_all():
                if str(getattr(exam, "exam_name", "")).strip() == target_name:
                    return int(exam.exam_id)
        except Exception:
            return None
        return None

    def _normalize_exam_date(self, value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""

        import re

        match = re.search(r"\d{4}-\d{2}-\d{2}", text)
        return match.group(0) if match else text

    def _build_analysis(
        self,
        results: list[Any],
        answer_records: list[Any],
        question_map: dict[int, Any],
    ) -> dict[str, Any]:
        student_count = len({result.student_id for result in results})
        average_score = self._average([float(result.score or 0) for result in results])
        if results:
            correct_rate, wrong_rate = self._result_correct_wrong_rates(results)
        elif answer_records:
            correct_rate = self._answer_record_correct_rate(answer_records)
            wrong_rate = self._answer_record_wrong_rate(answer_records)
        else:
            correct_rate = self._average([
                self._normalize_percent(result.accuracy)
                for result in results
            ])
            wrong_rate = max(100 - correct_rate, 0)

        question_rows = self._build_question_rows(answer_records, question_map)
        type_rows = self._build_group_rows(answer_records, question_map, "category", "type")
        sub_category_rows = self._build_group_rows(
            answer_records,
            question_map,
            "sub_category",
            "sub_category",
            empty_label="미분류",
        )
        difficulty_rows = self._build_group_rows(
            answer_records,
            question_map,
            "difficulty",
            "difficulty",
            empty_label="미분류",
        )

        if correct_rate >= 100 and wrong_rate <= 0:
            weak_type = ""
            feedback = ""
        else:
            weak_type = self._weakest_label(type_rows, "type")
            feedback = self._build_feedback(type_rows, sub_category_rows, difficulty_rows, question_rows)

        return {
            "summary": {
                "student_count": f"{student_count}명",
                "average_score": f"{average_score:.2f}점",
                "correct_rate": f"{correct_rate:.2f}%",
                "wrong_rate": f"{wrong_rate:.2f}%",
                "weak_type": weak_type,
            },
            "question_analysis": question_rows,
            "type_analysis": type_rows,
            "sub_category_analysis": sub_category_rows,
            "difficulty_analysis": difficulty_rows,
            "weakness_summary": {"feedback": feedback},
        }

    def _build_question_rows(
        self,
        answer_records: list[Any],
        question_map: dict[int, Any],
    ) -> list[dict[str, Any]]:
        grouped = self._group_records(answer_records, lambda record: record.question_id)
        rows = []

        for index, question_id in enumerate(sorted(grouped), start=1):
            records = grouped[question_id]
            question = question_map.get(question_id)
            correct_rate = self._record_rate(records)
            rows.append(
                {
                    "question_number": index,
                    "content": self._get_question_text(question, question_id),
                    "type": self._get_attr(question, "category", "미분류"),
                    "sub_category": self._get_attr(question, "sub_category", "미분류"),
                    "difficulty": self._get_attr(question, "difficulty", "미분류"),
                    "correct_rate": round(correct_rate, 2),
                    "wrong_rate": round(100 - correct_rate, 2),
                }
            )

        return rows

    def _build_group_rows(
        self,
        answer_records: list[Any],
        question_map: dict[int, Any],
        question_attr: str,
        output_key: str,
        empty_label: str = "미분류",
    ) -> list[dict[str, Any]]:
        grouped = self._group_records(
            answer_records,
            lambda record: self._get_attr(question_map.get(record.question_id), question_attr, empty_label),
        )
        rows = []

        for label in sorted(grouped):
            records = grouped[label]
            correct_rate = self._record_rate(records)
            rows.append(
                {
                    output_key: label,
                    "correct_rate": round(correct_rate, 2),
                    "wrong_rate": round(100 - correct_rate, 2),
                }
            )

        return rows

    def _filter_results_by_class(self, results: list[Any], class_id: Any) -> list[Any]:
        filtered = []
        for result in results:
            try:
                student = self.student_repository.read(result.student_id)
            except Exception:
                student = None
            if student and self._normalize_class_name(student.class_name) == self._normalize_class_name(class_id):
                filtered.append(result)
        return filtered

    def _get_registered_students(self, class_id: Any = None) -> list[Any]:
        try:
            if class_id not in (None, ""):
                students = self.student_repository.read_by_class(str(class_id), active_only=True)
                if students:
                    return list(students)

                normalized_class_id = self._normalize_class_name(class_id)
                students = [
                    student
                    for student in self.student_repository.read_all(active_only=True)
                    if self._normalize_class_name(getattr(student, "class_name", "")) == normalized_class_id
                ]
                students.sort(key=lambda student: str(getattr(student, "student_number", "")))
                return students

            students = list(self.student_repository.read_all(active_only=True))
            students.sort(key=lambda student: (
                str(getattr(student, "class_name", "")),
                str(getattr(student, "student_number", "")),
            ))
            return students
        except Exception:
            return []

    def _read_student(self, student_id: Any) -> Any:
        try:
            return self.student_repository.read(int(student_id))
        except Exception:
            return None

    def _get_question_map(self, exam_id: int, answer_records: list[Any]) -> dict[int, Any]:
        question_ids = set()

        try:
            question_ids.update(self.exam_question_repository.read_question_ids_by_exam(exam_id))
        except Exception:
            pass

        question_ids.update(record.question_id for record in answer_records)

        question_map = {}
        for question_id in question_ids:
            try:
                question = self.question_repository.read(question_id)
            except Exception:
                question = None
            if question:
                question_map[question_id] = question

        return question_map

    def _group_records(self, records: list[Any], key_getter: Any) -> dict[Any, list[Any]]:
        grouped = defaultdict(list)
        for record in records:
            grouped[key_getter(record)].append(record)
        return dict(grouped)

    def _record_rate(self, records: list[Any]) -> float:
        if not records:
            return 0.0
        correct_count = sum(1 for record in records if record.is_correct == CORRECT)
        return (correct_count / len(records)) * 100

    def _answer_record_correct_rate(self, records: list[Any]) -> float:
        return self._record_rate(records)

    def _answer_record_wrong_rate(self, records: list[Any]) -> float:
        if not records:
            return 0.0
        wrong_count = sum(1 for record in records if record.is_correct != CORRECT)
        return (wrong_count / len(records)) * 100

    def _result_correct_wrong_rates(self, results: list[Any]) -> tuple[float, float]:
        total_correct = sum(int(getattr(result, "correct_count", 0) or 0) for result in results)
        total_wrong = sum(int(getattr(result, "wrong_count", 0) or 0) for result in results)
        total_answered = total_correct + total_wrong
        if total_answered > 0:
            return (
                self._percent(total_correct, total_answered),
                self._percent(total_wrong, total_answered),
            )

        correct_rate = self._average([
            self._normalize_percent(getattr(result, "accuracy", 0))
            for result in results
        ])
        return correct_rate, max(100 - correct_rate, 0)

    def _normalize_percent(self, value: Any) -> float:
        number = float(value or 0)
        if 0 <= number <= 1:
            return number * 100
        return number

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _weakest_label(self, rows: list[dict[str, Any]], label_key: str) -> str:
        if not rows:
            return "-"
        weak_rows = [
            row
            for row in rows
            if float(row.get("correct_rate", 100) or 0) < 100
        ]
        if not weak_rows:
            return ""

        weakest = min(weak_rows, key=lambda row: float(row.get("correct_rate", 100)))
        return str(weakest.get(label_key, "-"))

    def _build_feedback(
        self,
        type_rows: list[dict[str, Any]],
        sub_category_rows: list[dict[str, Any]],
        difficulty_rows: list[dict[str, Any]],
        question_rows: list[dict[str, Any]],
    ) -> str:
        weak_type = self._weakest_label(type_rows, "type")
        weak_sub_category = self._weakest_label(sub_category_rows, "sub_category")
        weak_difficulty = self._weakest_label(difficulty_rows, "difficulty")
        weak_questions = [
            str(row.get("question_number"))
            for row in sorted(
                [
                    row
                    for row in question_rows
                    if float(row.get("correct_rate", 100) or 0) < 100
                ],
                key=lambda row: float(row.get("correct_rate", 100)),
            )[:3]
        ]

        parts = []
        if weak_type and weak_type != "-":
            parts.append(f"{weak_type} 유형의 정답률이 가장 낮습니다")
        if weak_sub_category and weak_sub_category != "-":
            parts.append(f"{weak_sub_category} 세부 분류를 우선 보강하세요")
        if weak_difficulty and weak_difficulty != "-":
            parts.append(f"{weak_difficulty} 난이도 문항을 추가 복습하면 좋습니다")
        if weak_questions:
            parts.append(f"오답률이 높은 문항: {', '.join(weak_questions)}번")

        if parts:
            return ". ".join(parts) + "."
        if type_rows or sub_category_rows or difficulty_rows or question_rows:
            return ""
        return "분석할 결과 데이터가 없습니다."

    def _get_question_text(self, question: Any, question_id: int) -> str:
        text = self._get_attr(question, "question_text", "")
        return text or f"{question_id}번 문항"

    def _get_attr(self, item: Any, attr_name: str, default: Any = "") -> Any:
        if not item:
            return default
        value = getattr(item, attr_name, default)
        if value in (None, ""):
            return default
        return value

    def _normalize_class_name(self, value: Any) -> str:
        return str(value or "").replace(" ", "").strip()

    def _empty_dashboard(
        self,
        message: str,
        exam_id: Any = None,
        class_id: Any = None,
        exam_date: Any = None,
        exam: Any = None,
    ) -> dict[str, Any]:
        summary = {
            "student_count": 0,
            "total_questions": int(getattr(exam, "total_questions", 0) or 0),
            "average_score": 0.0,
            "overall_accuracy": 0.0,
            "average_correct_count": 0.0,
        }
        return {
            "success": False,
            "message": message,
            "filters": {
                "exam_id": exam_id,
                "exam_name": getattr(exam, "exam_name", ""),
                "class_id": class_id,
                "class_name": class_id or getattr(exam, "target_class", ""),
                "exam_date": exam_date or getattr(exam, "exam_date", ""),
            },
            "summary": summary,
            "question_accuracy": [],
            "category_accuracy": [],
            "subcategory_accuracy_top5": [],
            "difficulty_accuracy": [],
            "student_results": [],
            "metrics": self._build_dashboard_metrics(summary),
            "charts": self._build_dashboard_chart_payload([], [], [], []),
        }

    def _empty_analysis(self) -> dict[str, Any]:
        return {
            "summary": {
                "student_count": "0명",
                "average_score": "0.00점",
                "correct_rate": "0.00%",
                "wrong_rate": "0.00%",
                "weak_type": "-",
            },
            "question_analysis": [],
            "type_analysis": [],
            "sub_category_analysis": [],
            "difficulty_analysis": [],
            "weakness_summary": {
                "feedback": "분석할 결과 데이터가 없습니다."
            },
        }
