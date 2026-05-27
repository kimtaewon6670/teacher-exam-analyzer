from __future__ import annotations

import random
from typing import Any

from app.models.exam_builder_model import ExamBuildItem
from app.models.question_model import Question


class ExamBuilderService:
    DEFAULT_QUESTION_TYPES = ("어휘", "문법", "독해")
    DEFAULT_DIFFICULTIES = ("쉬움", "중간", "어려움")

    def __init__(self, question_repository) -> None:
        self.question_repository = question_repository
        self.last_build_summary: dict[str, Any] = {}

    def create_random_exam(self, criteria: dict[str, Any]) -> list[Question]:
        """
        시험 생성 공통 진입점.
        cart_items가 있으면 장바구니 방식으로, 없으면 기존 category_counts/difficulty_counts 방식으로 생성한다.
        """
        if criteria.get("cart_items"):
            return self.create_exam_from_cart(criteria)

        return self.create_exam_from_counts(criteria)

    def create_exam_from_counts(self, criteria: dict[str, Any]) -> list[Question]:
        candidates = self._get_candidates(criteria)
        selected_questions: list[Question] = []
        selected_ids: set[int] = set()
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

    def create_exam_from_cart(self, criteria: dict[str, Any]) -> list[Question]:
        """
        장바구니 행 기준으로 시험 문제를 생성한다.
        각 행은 분류, 총 개수, 난이도별 직접 입력 개수를 가질 수 있다.
        """
        cart_items = self.normalize_cart_items(criteria.get("cart_items", []))
        selected_questions: list[Question] = []
        selected_ids: set[int] = set()
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

    def _get_candidates(
        self,
        criteria: dict[str, Any],
        category: str | None = None,
        difficulty: str | None = None,
    ) -> list[Question]:
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

        if candidates:
            return candidates

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


class PdfExportService:
    def export_exam_pdf(self, file_path, exam_info, questions):
        """PDF generation logic."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4

            c = canvas.Canvas(file_path, pagesize=A4)
            c.drawString(100, 800, f"Test Title: {exam_info.get('title')}")
            for i, question in enumerate(questions, 1):
                c.drawString(100, 800 - (i * 30), f"{i}. {question.question_text}")

            c.save()
            return True, "저장 완료"
        except Exception as exc:
            return False, str(exc)
