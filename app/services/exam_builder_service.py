from __future__ import annotations

import random

from app.models.question_model import Question


class ExamBuilderService:
    def __init__(self, question_repository) -> None:
        self.question_repository = question_repository

    def create_random_exam(self, criteria: dict) -> list[Question]:
        candidates = self.question_repository.read_all(active_only=True)
        candidates = self._filter_questions(candidates, criteria)

        selected_questions: list[Question] = []
        selected_ids: set[int] = set()

        for category, count in criteria.get("category_counts", {}).items():
            category_candidates = [
                question
                for question in candidates
                if question.category == category and question.question_id not in selected_ids
            ]
            selected_questions.extend(self._sample_questions(category_candidates, count, selected_ids))

        for difficulty, count in criteria.get("difficulty_counts", {}).items():
            difficulty_candidates = [
                question
                for question in candidates
                if question.difficulty == difficulty and question.question_id not in selected_ids
            ]
            selected_questions.extend(self._sample_questions(difficulty_candidates, count, selected_ids))

        total_count = criteria.get("total_count", 0)
        if total_count and len(selected_questions) < total_count:
            remaining_candidates = [
                question for question in candidates if question.question_id not in selected_ids
            ]
            selected_questions.extend(
                self._sample_questions(remaining_candidates, total_count - len(selected_questions), selected_ids)
            )

        return selected_questions[:total_count] if total_count else selected_questions

    def _filter_questions(self, questions: list[Question], criteria: dict) -> list[Question]:
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

    def _sample_questions(self, candidates: list[Question], count: int, selected_ids: set[int]) -> list[Question]:
        if count <= 0 or not candidates:
            return []

        selected = random.sample(candidates, min(count, len(candidates)))
        for question in selected:
            if question.question_id is not None:
                selected_ids.add(question.question_id)
        return selected
