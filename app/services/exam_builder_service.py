from __future__ import annotations

import random
from typing import Any

from app.models.exam_builder_model import ExamBuildItem
from app.models.question_model import Question


class ExamBuilderService:
    DEFAULT_QUESTION_TYPES = ("어휘", "문법", "독해")
    DEFAULT_DIFFICULTIES = ("쉬움", "보통", "어려움")

    def __init__(self, question_repository) -> None:
        self.question_repository = question_repository
        self.last_build_summary: dict[str, Any] = {}

    def create_random_exam(self, criteria: dict[str, Any]) -> list[Question]:
        """
        시험 생성 공통 진입점.
        cart_items가 있으면 장바구니 방식으로, 없으면 기존 category_counts/difficulty_counts 방식으로 생성한다.
        """
        selected_questions = self._get_selected_questions(criteria)
        selected_ids = {
            question.question_id for question in selected_questions if question.question_id is not None
        }

        if criteria.get("cart_items"):
            auto_questions = self.create_exam_from_cart(criteria, selected_ids=selected_ids)
        else:
            auto_questions = self.create_exam_from_counts(criteria, selected_ids=selected_ids)

        combined_questions = self._deduplicate_questions([*selected_questions, *auto_questions])
        if selected_questions:
            self.last_build_summary["manual_selected_count"] = len(selected_questions)
            self.last_build_summary["selected_count"] = len(combined_questions)
            self.last_build_summary["requested_count"] = (
                self.last_build_summary.get("requested_count", 0) + len(selected_questions)
            )
            self.last_build_summary["shortage"] = max(
                self.last_build_summary.get("requested_count", 0) - len(combined_questions),
                0,
            )
        return combined_questions

    def create_exam_from_counts(
        self,
        criteria: dict[str, Any],
        selected_ids: set[int] | None = None,
    ) -> list[Question]:
        candidates = self._get_candidates(criteria)
        selected_questions: list[Question] = []
        selected_ids = selected_ids or set()
        summary_items = []

        for category, count in criteria.get("category_counts", {}).items():
            category_count = self._to_count(count)
            category_candidates = [
                question
                for question in candidates
                if question.category == category and question.question_id not in selected_ids
            ]
            selected = self._sample_questions(category_candidates, category_count, selected_ids)
            selected_questions.extend(selected)
            summary_items.append(
                self._build_summary_item(category, category_count, len(selected), {})
            )

        for difficulty, count in criteria.get("difficulty_counts", {}).items():
            difficulty_count = self._to_count(count)
            difficulty_candidates = [
                question
                for question in candidates
                if question.difficulty == difficulty and question.question_id not in selected_ids
            ]
            selected = self._sample_questions(difficulty_candidates, difficulty_count, selected_ids)
            selected_questions.extend(selected)
            summary_items.append(
                self._build_summary_item(difficulty, difficulty_count, len(selected), {})
            )

        total_count = self._to_count(criteria.get("total_count", criteria.get("count", 0)))
        if total_count and len(selected_questions) < total_count:
            remaining_candidates = [
                question for question in candidates if question.question_id not in selected_ids
            ]
            selected_questions.extend(
                self._sample_questions(
                    remaining_candidates,
                    total_count - len(selected_questions),
                    selected_ids,
                )
            )

        if total_count:
            selected_questions = selected_questions[:total_count]

        requested_count = total_count or sum(item["requested_count"] for item in summary_items)
        self.last_build_summary = {
            "requested_count": requested_count,
            "selected_count": len(selected_questions),
            "shortage": max(requested_count - len(selected_questions), 0),
            "items": summary_items,
        }
        return selected_questions

    def create_exam_from_cart(
        self,
        criteria: dict[str, Any],
        selected_ids: set[int] | None = None,
    ) -> list[Question]:
        """
        장바구니 행 기준으로 시험 문제를 생성한다.
        각 행은 분류, 총 개수, 난이도별 직접 입력 개수를 가질 수 있다.
        """
        cart_items = self.normalize_cart_items(criteria.get("cart_items", []))
        selected_questions: list[Question] = []
        selected_ids = selected_ids or set()
        summary_items = []

        for item in cart_items:
            item_questions, item_summary = self._select_questions_for_item(
                item,
                criteria,
                selected_ids,
            )
            selected_questions.extend(item_questions)
            summary_items.append(item_summary)

        self.last_build_summary = {
            "requested_count": sum(item.total_count for item in cart_items),
            "selected_count": len(selected_questions),
            "shortage": sum(item["shortage"] for item in summary_items),
            "items": summary_items,
        }
        return selected_questions

    def normalize_cart_items(self, raw_items: list[Any]) -> list[ExamBuildItem]:
        items = []
        for raw_item in raw_items:
            if isinstance(raw_item, ExamBuildItem):
                item = raw_item
            elif isinstance(raw_item, dict):
                item = ExamBuildItem.from_dict(raw_item)
            else:
                continue

            if not item.is_empty():
                items.append(item)

        return items

    def get_last_build_summary(self) -> dict[str, Any]:
        return self.last_build_summary

    def get_filter_options(self) -> dict[str, list[str]]:
        """
        Return exam-builder filter options for the controller to inject into the View.

        TODO: Replace DEFAULT_QUESTION_TYPES with Repository-provided categories when
        category master data or question metadata lookup is connected.
        """
        return {
            "question_types": list(self.DEFAULT_QUESTION_TYPES),
        }

    def validate_exam_request(self, criteria: dict[str, Any]) -> tuple[bool, str]:
        """Validate requested auto-extraction counts against currently available questions."""
        selected_ids = set(self._to_id_list(criteria.get("selected_question_ids", [])))
        validation_items = self._get_validation_items(criteria)

        for item in validation_items:
            available_count = self.count_available_questions(
                criteria,
                category=item.get("category"),
                difficulty=item.get("difficulty"),
                excluded_question_ids=selected_ids,
            )
            requested_count = self._to_count(item.get("count"))
            if requested_count > available_count:
                label_parts = [part for part in (item.get("category"), item.get("difficulty")) if part]
                label = " / ".join(label_parts) or "현재 조건"
                return (
                    False,
                    f"{label} 조건으로 추출 가능한 문제는 최대 {available_count}문항입니다. "
                    f"요청 문항 수를 {available_count}문항 이하로 줄여주세요.",
                )

        return True, ""

    def count_available_questions(
        self,
        criteria: dict[str, Any],
        category: str | None = None,
        difficulty: str | None = None,
        excluded_question_ids: set[int] | None = None,
    ) -> int:
        excluded_question_ids = excluded_question_ids or set()
        candidates = self._get_candidates(criteria, category=category, difficulty=difficulty)
        return len(
            [
                question
                for question in candidates
                if question.question_id is None or question.question_id not in excluded_question_ids
            ]
        )

    def get_selectable_questions(self, criteria: dict[str, Any] | None = None) -> list[Question]:
        """Return active questions for the direct-selection dialog."""
        criteria = criteria or {}
        return self._get_candidates(criteria)

    def _select_questions_for_item(
        self,
        item: ExamBuildItem,
        criteria: dict[str, Any],
        selected_ids: set[int],
    ) -> tuple[list[Question], dict[str, Any]]:
        selected: list[Question] = []
        remaining_budget = item.total_count

        for difficulty, count in item.difficulty_counts.items():
            if remaining_budget <= 0:
                break

            requested_count = min(self._to_count(count), remaining_budget)
            selected.extend(
                self._select_candidates(
                    criteria=criteria,
                    category=item.category,
                    difficulty=difficulty,
                    count=requested_count,
                    selected_ids=selected_ids,
                )
            )
            remaining_budget = item.total_count - len(selected)

        remaining_count = min(item.unspecified_count(), remaining_budget)
        if remaining_count:
            selected.extend(
                self._select_candidates(
                    criteria=criteria,
                    category=item.category,
                    difficulty=None,
                    count=remaining_count,
                    selected_ids=selected_ids,
                )
            )

        return selected, self._build_summary_item(
            label=item.category,
            requested_count=item.total_count,
            selected_count=len(selected),
            difficulty_counts=item.difficulty_counts,
        )

    def _select_candidates(
        self,
        criteria: dict[str, Any],
        category: str,
        difficulty: str | None,
        count: int,
        selected_ids: set[int],
    ) -> list[Question]:
        if count <= 0:
            return []

        candidates = self._get_candidates(criteria, category=category, difficulty=difficulty)
        candidates = [
            question
            for question in candidates
            if question.question_id is None or question.question_id not in selected_ids
        ]
        return self._sample_questions(candidates, count, selected_ids)

    def _get_selected_questions(self, criteria: dict[str, Any]) -> list[Question]:
        questions = criteria.get("selected_questions")
        if questions:
            return [
                question
                for question in questions
                if isinstance(question, Question) or hasattr(question, "question_id")
            ]

        question_ids = self._to_id_list(criteria.get("selected_question_ids", []))
        selected = []
        for question_id in question_ids:
            question = self._read_question(question_id)
            if question:
                selected.append(question)
        return selected

    def _read_question(self, question_id: int) -> Question | None:
        try:
            return self.question_repository.read(question_id)
        except Exception:
            return next(
                (question for question in self._get_sample_pool() if question.question_id == question_id),
                None,
            )

    def _deduplicate_questions(self, questions: list[Question]) -> list[Question]:
        deduplicated = []
        seen_ids = set()
        for question in questions:
            question_id = getattr(question, "question_id", None)
            if question_id is not None:
                if question_id in seen_ids:
                    continue
                seen_ids.add(question_id)
            deduplicated.append(question)
        return deduplicated

    def _get_validation_items(self, criteria: dict[str, Any]) -> list[dict[str, Any]]:
        cart_items = self.normalize_cart_items(criteria.get("cart_items", []))
        if cart_items:
            items = []
            for item in cart_items:
                specified_count = 0
                for difficulty, count in item.difficulty_counts.items():
                    count = self._to_count(count)
                    specified_count += count
                    if count:
                        items.append(
                            {
                                "category": item.category,
                                "difficulty": difficulty,
                                "count": count,
                            }
                        )

                unspecified_count = max(item.total_count - specified_count, 0)
                if unspecified_count:
                    items.append(
                        {
                            "category": item.category,
                            "difficulty": None,
                            "count": unspecified_count,
                        }
                    )
            return items

        items = []
        for category, count in criteria.get("category_counts", {}).items():
            items.append({"category": category, "difficulty": None, "count": count})
        for difficulty, count in criteria.get("difficulty_counts", {}).items():
            items.append({"category": None, "difficulty": difficulty, "count": count})
        if not items and self._to_count(criteria.get("total_count", criteria.get("count", 0))):
            items.append(
                {
                    "category": criteria.get("category") or criteria.get("type"),
                    "difficulty": criteria.get("difficulty"),
                    "count": criteria.get("total_count", criteria.get("count", 0)),
                }
            )
        return items

    def _get_candidates(
        self,
        criteria: dict[str, Any],
        category: str | None = None,
        difficulty: str | None = None,
    ) -> list[Question]:
        try:
            if hasattr(self.question_repository, "get_questions_by_filter"):
                candidates = self.question_repository.get_questions_by_filter(
                    category=category or criteria.get("category") or criteria.get("type"),
                    difficulty=difficulty or criteria.get("difficulty"),
                    exam_name=criteria.get("exam_name"),
                    class_name=criteria.get("class_name"),
                    sub_category=criteria.get("sub_category"),
                )
            else:
                candidates = self.question_repository.read_all(active_only=True)
                candidates = self._filter_by_category_and_difficulty(
                    candidates,
                    category=category or criteria.get("category") or criteria.get("type"),
                    difficulty=difficulty or criteria.get("difficulty"),
                )

            candidates = self._filter_by_common_criteria(candidates, criteria)
            if candidates or self._repository_has_questions():
                return candidates
        except Exception:
            pass

        return self._filter_by_common_criteria(
            self._filter_by_category_and_difficulty(
                self._get_sample_pool(),
                category=category or criteria.get("category") or criteria.get("type"),
                difficulty=difficulty or criteria.get("difficulty"),
            ),
            criteria,
        )

    def _filter_by_common_criteria(
        self,
        questions: list[Question],
        criteria: dict[str, Any],
    ) -> list[Question]:
        sub_category = criteria.get("sub_category", "")
        tag = criteria.get("tag", "")

        filtered_questions = questions
        if sub_category:
            filtered_questions = [
                question for question in filtered_questions if question.sub_category == sub_category
            ]
        if tag:
            filtered_questions = [
                question for question in filtered_questions if tag in (question.tags or "")
            ]

        return filtered_questions

    def _filter_by_category_and_difficulty(
        self,
        questions: list[Question],
        category: str | None = None,
        difficulty: str | None = None,
    ) -> list[Question]:
        return [
            question
            for question in questions
            if (not category or question.category == category)
            and (not difficulty or question.difficulty == difficulty)
        ]

    def _sample_questions(
        self,
        candidates: list[Question],
        count: int,
        selected_ids: set[int],
    ) -> list[Question]:
        if count <= 0 or not candidates:
            return []

        selected = random.sample(candidates, min(count, len(candidates)))
        for question in selected:
            if question.question_id is not None:
                selected_ids.add(question.question_id)
        return selected

    def _get_sample_pool(self) -> list[Question]:
        """DB 연결 전 샘플 문제 영역. Repository 연결 후 제거하기 쉽도록 분리했다."""
        samples = []
        question_id = 1
        categories = ("어휘", "문법", "독해")

        for category in categories:
            for difficulty in self.DEFAULT_DIFFICULTIES:
                for index in range(1, 8):
                    samples.append(
                        Question(
                            question_id=question_id,
                            question_text=f"{category} {difficulty} 샘플 문제 {index}",
                            category=category,
                            difficulty=difficulty,
                            answer_text="정답",
                        )
                    )
                    question_id += 1

        return samples

    def _build_summary_item(
        self,
        label: str,
        requested_count: int,
        selected_count: int,
        difficulty_counts: dict[str, int],
    ) -> dict[str, Any]:
        return {
            "category": label,
            "requested_count": requested_count,
            "selected_count": selected_count,
            "shortage": max(requested_count - selected_count, 0),
            "difficulty_counts": dict(difficulty_counts),
        }

    def _to_count(self, value: Any) -> int:
        if value in (None, ""):
            return 0

        try:
            return max(int(value), 0)
        except (TypeError, ValueError):
            return 0

    def _to_id_list(self, values: Any) -> list[int]:
        if values in (None, ""):
            return []
        if not isinstance(values, (list, tuple, set)):
            values = [values]

        ids = []
        for value in values:
            try:
                ids.append(int(value))
            except (TypeError, ValueError):
                continue
        return ids

    def _repository_has_questions(self) -> bool:
        try:
            return bool(self.question_repository.read_all(active_only=True))
        except Exception:
            return False


class PdfExportService:
    def export_exam_pdf(self, file_path, exam_info, questions):
        """Compatibility wrapper for older imports."""
        from app.services.pdf_export_service import PdfExportService as ReportPdfExportService

        return ReportPdfExportService().export_exam_pdf(file_path, exam_info, questions)
