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

    SAMPLE_EXAMS = [
        {"id": 1, "name": "2024년 1학기 중간고사"},
        {"id": 2, "name": "2024년 1학기 기말고사"},
    ]
    SAMPLE_CLASSES = [
        {"id": "1-1", "name": "1학년 1반"},
        {"id": "1-2", "name": "1학년 2반"},
        {"id": "1-3", "name": "1학년 3반"},
    ]

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

        # TODO: Repository 연결이 안정화되면 화면 확인용 샘플데이터 제거.
        return list(self.SAMPLE_EXAMS)

    def get_class_options(self) -> list[dict[str, Any]]:
        class_ids = []
        try:
            for student in self.student_repository.read_all(active_only=True):
                if student.class_name and student.class_name not in class_ids:
                    class_ids.append(student.class_name)
        except Exception:
            pass

        if class_ids:
            return [{"id": class_id, "name": str(class_id)} for class_id in class_ids]

        # TODO: 별도 Class Repository가 추가되면 여기에서 반 목록을 조회하도록 교체.
        return list(self.SAMPLE_CLASSES)

    def analyze(self, filters: dict[str, Any]) -> dict[str, Any]:
        exam_id = filters.get("exam_id")
        class_id = filters.get("class_id")

        if exam_id is None:
            return self._sample_analysis()

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

        return self._sample_analysis()

    def _build_analysis(
        self,
        results: list[Any],
        answer_records: list[Any],
        question_map: dict[int, Any],
    ) -> dict[str, Any]:
        student_count = len({result.student_id for result in results})
        average_score = self._average([float(result.score or 0) for result in results])
        correct_rate = self._average([float(result.accuracy or 0) * 100 for result in results])
        if not results and answer_records:
            correct_rate = self._answer_record_correct_rate(answer_records)
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
            if student and student.class_name == class_id:
                filtered.append(result)
        return filtered

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

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _weakest_label(self, rows: list[dict[str, Any]], label_key: str) -> str:
        if not rows:
            return "-"
        weakest = min(rows, key=lambda row: float(row.get("correct_rate", 100)))
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
            for row in sorted(question_rows, key=lambda row: float(row.get("correct_rate", 100)))[:3]
        ]

        parts = []
        if weak_type != "-":
            parts.append(f"{weak_type} 유형의 정답률이 가장 낮습니다")
        if weak_sub_category != "-":
            parts.append(f"{weak_sub_category} 세부 분류를 우선 보강하세요")
        if weak_difficulty != "-":
            parts.append(f"{weak_difficulty} 난이도 문항을 추가 복습하면 좋습니다")
        if weak_questions:
            parts.append(f"오답률이 높은 문항: {', '.join(weak_questions)}번")

        return ". ".join(parts) + ("." if parts else "분석할 결과 데이터가 없습니다.")

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

    def _sample_analysis(self) -> dict[str, Any]:
        # TODO: 실제 Repository 데이터가 준비되면 화면 확인용 샘플데이터 제거.
        return {
            "summary": {
                "student_count": "28명",
                "average_score": "72.35점",
                "correct_rate": "72.45%",
                "wrong_rate": "27.55%",
                "weak_type": "문법",
            },
            "question_analysis": [
                {
                    "question_number": 1,
                    "content": "빈칸에 들어갈 알맞은 단어",
                    "type": "어휘",
                    "sub_category": "동의어",
                    "difficulty": "쉬움",
                    "correct_rate": 85.1,
                    "wrong_rate": 14.9,
                },
                {
                    "question_number": 2,
                    "content": "문장에서 틀린 부분 찾기",
                    "type": "문법",
                    "sub_category": "시제",
                    "difficulty": "보통",
                    "correct_rate": 58.3,
                    "wrong_rate": 41.7,
                },
                {
                    "question_number": 3,
                    "content": "글의 주제 찾기",
                    "type": "독해",
                    "sub_category": "주제",
                    "difficulty": "어려움",
                    "correct_rate": 52.0,
                    "wrong_rate": 48.0,
                },
            ],
            "type_analysis": [
                {"type": "어휘", "correct_rate": 78.1, "wrong_rate": 21.9},
                {"type": "문법", "correct_rate": 65.2, "wrong_rate": 34.8},
                {"type": "독해", "correct_rate": 74.3, "wrong_rate": 25.7},
            ],
            "sub_category_analysis": [
                {"sub_category": "동의어", "correct_rate": 85.1, "wrong_rate": 14.9},
                {"sub_category": "시제", "correct_rate": 58.3, "wrong_rate": 41.7},
                {"sub_category": "주제 찾기", "correct_rate": 72.6, "wrong_rate": 27.4},
            ],
            "difficulty_analysis": [
                {"difficulty": "쉬움", "correct_rate": 85.1, "wrong_rate": 14.9},
                {"difficulty": "보통", "correct_rate": 72.4, "wrong_rate": 27.6},
                {"difficulty": "어려움", "correct_rate": 56.3, "wrong_rate": 43.7},
            ],
            "weakness_summary": {
                "feedback": "문법 유형과 어려움 난이도 문항에서 정답률이 낮습니다. 시제 관련 문항을 우선 복습하고 유사 문항을 추가 연습하세요."
            },
        }
